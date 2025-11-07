"""Post model."""

import datetime
import logging
from collections.abc import Iterable
from typing import TYPE_CHECKING, TypedDict

from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Case, IntegerField, Max, Q, Value, When
from django.db.transaction import on_commit
from django.utils import timezone
from django.utils.text import slugify

from djpress.conf import settings as djpress_settings
from djpress.exceptions import PageNotFoundError, PostNotFoundError
from djpress.models.category import Category
from djpress.models.tag import Tag
from djpress.plugins import registry
from djpress.plugins.hook_registry import POST_RENDER_CONTENT, POST_SAVE_POST, PRE_RENDER_CONTENT, SEARCH_CONTENT
from djpress.utils import get_markdown_renderer

logger = logging.getLogger(__name__)

render_markdown = get_markdown_renderer()


PUBLISHED_POSTS_CACHE_KEY = "published_posts"


class PageNode(TypedDict):
    """Type for representing a page node in the page tree."""

    page: "Post"
    children: list["PageNode"]


class AdminManager(models.Manager):
    """Manager that returns all posts/pages - used only by admin."""

    def get_queryset(self) -> models.QuerySet:
        """Return completely unfiltered queryset."""
        return super().get_queryset()


class PostsAndPagesManager(models.Manager):
    """Default manager that only returns published content."""

    def get_queryset(self) -> models.QuerySet:
        """Return only published posts and pages."""
        return (
            super()
            .get_queryset()
            .filter(
                status="published",
                published_at__lte=timezone.now(),
            )
        )

    def search(self, query: str = "") -> models.QuerySet:
        """Search interface.

        Provides a swappable search method. The default search is the `_generic_search` method.

        Args:
            query (str): The search query.

        Returns:
            models.QuerySet: The filtered queryset.
        """
        qs = self.get_queryset()

        if not query:
            return qs.none()

        # Allow plugins to override the search method
        results: models.QuerySet = registry.run_hook(SEARCH_CONTENT, query)

        if not isinstance(results, models.QuerySet):
            results = self._generic_search(query)

        return results

    def _generic_search(self, query: str) -> models.QuerySet:
        """Search for posts/pages by title or content.

        This is intentionally simple for now and only supports searching for specific terms.

        This search method uses a combination of title and content matching to find relevant posts/pages.

        It uses a basic "weighting" to prioritise content that matches the query in the title over the content.

        Args:
            query (str): The search query.

        Returns:
            models.QuerySet: The filtered queryset.
        """
        qs = self.get_queryset()

        if not query:
            return qs.none()

        """
        The queries that are performed on the each field.
        We keep this simple to work across all database types.
        """
        title_match = Q(title__icontains=query)
        content_match = Q(content__icontains=query)

        """
        Assigning weights to title and content matches let's us prioritise titles that match over content.
        Additional weights can be added in the future if we want to include other aspects of the post to search on.
        """
        title_weight = 2
        content_weight = 1

        """
        This annotates each post and page with a score based on where the match occurs.
        Each post and page will have a score of 0, 1, or 2.
        And then any posts/pages with a score of 0 are filtered out.
        """
        qs = qs.annotate(
            score=Case(
                When(title_match, then=Value(title_weight)),
                When(content_match, then=Value(content_weight)),
                default=Value(0),
                output_field=IntegerField(),
            ),
        ).filter(score__gt=0)

        """
        Sorting:

        1. Score: Higher score means more relevant results.
        2. Post Type: Prioritise pages over posts.
        3. Updated at date: More recent posts are prioritised.
        """
        return qs.order_by("-score", "post_type", "-updated_at")


class PagesManager(models.Manager):
    """Page custom manager."""

    def get_queryset(self) -> models.QuerySet:
        """Return the queryset for pages."""
        return (
            super()
            .get_queryset()
            .filter(
                post_type="page",
                status="published",
                published_at__lte=timezone.now(),
            )
            .order_by("menu_order", "title")
        )

    def get_published_pages(self) -> models.QuerySet:
        """Return all published pages.

        For a page to be considered published, it must meet the following requirements:
        - The status must be "published".
        - The date must be less than or equal to the current date/time.
        - All parent pages must also be published.
        """
        return Post.page_objects.filter(
            pk__in=[page.pk for page in self.get_queryset() if page.is_published],
        ).order_by("menu_order", "title", "-published_at")

    def get_published_page_by_slug(
        self,
        slug: str,
    ) -> "Post":
        """Return a single published page.

        Args:
            slug (str): The slug of the page.

        Returns:
            Post: The published page.
        """
        try:
            page: Post = self.get_published_pages().get(slug=slug)
        except Post.DoesNotExist as exc:
            msg = "Page not found"
            raise PageNotFoundError(msg) from exc

        return page

    def get_published_page_by_path(
        self,
        path: str,
    ) -> "Post":
        """Return a single published page from a path.

        The path can consist of one or more pages, e.g. "about", "about/contact". We split the path into parts and
        check the page is valid. These are the checks to be made:

        1. The first part of the path must be a top-level page.
        2. Subsequent parts must be children of the previous page.
        3. The final page must be published.

        Args:
            path (str): The path to the page.

        Returns:
            Post: The published page.

        Raises:
            PageNotFoundError: If the page cannot be found.
        """
        # Strip leading and trailing slashes and split the path into parts
        path_parts = path.strip("/").split("/")

        for i, slug in enumerate(path_parts):
            if i == 0:
                try:
                    # The first item must be a top-level page
                    current_page: Post = self.get(slug=slug, parent__isnull=True)
                except Post.DoesNotExist as exc:
                    msg = "Page not found"
                    raise PageNotFoundError(msg) from exc
            else:
                try:
                    # Subsequent items must be children of the previous page
                    current_page: Post = self.get(slug=slug, parent=current_page)
                except Post.DoesNotExist as exc:
                    msg = "Page not found"
                    raise PageNotFoundError(msg) from exc

        return current_page

    def get_page_tree(self) -> list[PageNode]:
        """Return the page tree.

        This returns a list of top-level pages. Each page is a dict containing the Post object and a list of children.

        Used to build the page hierarchy.

        ```
        root_pages = [
            {
                'page': <Page object>,
                'children': [
                    {
                        'page': <Child Page object>,
                        'children': [
                            {
                                'page': <Grandchild Page object>,
                                'children': []
                            },
                            # ... more grandchildren ...
                        ]
                    },
                    # ... more children ...
                ]
            },
            # ... more root pages ...
        ]
        ```

        Returns:
            PageNode: A list of top-level pages - each page is a dict containing the Post object
            and a list of children. Each child is a dict containing the Post object and a list of children, and so on.
        """
        pages: models.QuerySet[Post] = self.get_published_pages().select_related("parent")
        page_dict = {page.pk: {"page": page, "children": []} for page in pages}
        root_pages = []
        for page_data in page_dict.values():
            page = page_data["page"]
            if page.parent:
                page_dict[page.parent.pk]["children"].append(page_data)

            else:
                root_pages.append(page_data)
        return root_pages


class PostsManager(models.Manager):
    """Post custom manager."""

    def get_queryset(self) -> models.QuerySet:
        """Return the queryset for posts.

        Note: this queryset is mirrored in both the Tag and Category models. If this logic changes, it should be
        reflected in those models as well.
        """
        return (
            super()
            .get_queryset()
            .filter(
                post_type="post",
                status="published",
                published_at__lte=timezone.now(),
            )
            .order_by("-published_at")
        )

    def get_published_posts(self) -> models.QuerySet:
        """Returns all published posts.

        For a post to be considered published, it must meet the following requirements:
        - The status must be "published".
        - The date must be less than or equal to the current date/time.
        """
        return self.get_queryset().prefetch_related("categories", "author")

    def get_recent_published_posts(self) -> models.QuerySet:
        """Return recent published posts.

        This does not return a paginated queryset. Use get_paginated_published_posts
        instead.

        If CACHE_RECENT_PUBLISHED_POSTS is set to True, we return the cached queryset.
        """
        if djpress_settings.CACHE_RECENT_PUBLISHED_POSTS:
            return self._get_cached_recent_published_posts()

        return self.get_published_posts()[: djpress_settings.RECENT_PUBLISHED_POSTS_COUNT]

    def _get_cached_recent_published_posts(self) -> models.QuerySet:
        """Return the cached recent published posts queryset.

        If there are any future posts, we calculate the seconds until that post, then we
        set the timeout to that number of seconds.
        """
        queryset = cache.get(PUBLISHED_POSTS_CACHE_KEY)

        # Check if the cache is empty or if the length of the queryset is not equal to the number of recent posts. If
        # the length is different it means the setting may have changed.
        if queryset is None or len(queryset) != djpress_settings.RECENT_PUBLISHED_POSTS_COUNT:
            # Get the queryset from the database for all published posts, including those in the future. Then we
            # calculate the timeout to set, and then filter the queryset to only include the recent published posts.
            # Note: we use admin_objects here to get all posts, including those in the future.
            queryset = (
                self.model.admin_objects.filter(post_type="post", status="published")
                .prefetch_related(
                    "categories",
                    "author",
                )
                .order_by("-published_at")
            )
            timeout = self._get_cache_timeout(queryset)
            queryset = queryset.filter(published_at__lte=timezone.now())[
                : djpress_settings.RECENT_PUBLISHED_POSTS_COUNT
            ]

            cache.set(
                PUBLISHED_POSTS_CACHE_KEY,
                queryset,
                timeout=timeout,
            )

        return queryset

    def _get_cache_timeout(
        self,
        queryset: models.QuerySet,
    ) -> int | None:
        """Return the timeout for the cache.

        If there are any future posts, we calculate the seconds until that post.

        Args:
            queryset: The queryset of published posts.

        Returns:
            int | None: The number of seconds until the next future post, or None if
            there are no future posts.
        """
        # TODO: total_seconds returns a float not an int.
        future_posts = queryset.filter(published_at__gt=timezone.now())
        if future_posts.exists():
            future_post = future_posts[0]
            return int((future_post.published_at - timezone.now()).total_seconds())

        return None

    def get_published_post_by_slug(
        self,
        slug: str,
        year: int | None = None,
        month: int | None = None,
        day: int | None = None,
    ) -> "Post":
        """Return a single published post.

        Args:
            slug (str): The post slug.
            year (int | None): The year.
            month (int | None): The month.
            day (int | None): The day.

        Returns:
            Post: The published post.

        Raises:
            PostNotFoundError: If the post is not found in the database.
        """
        # TODO: try to get the post from the cache

        filters = {"slug": slug}

        if year:
            filters["published_at__year"] = str(year)

        if month:
            filters["published_at__month"] = str(month)

        if day:
            filters["published_at__day"] = str(day)

        try:
            return self.get_published_posts().get(**filters)
        except Post.DoesNotExist as exc:
            msg = "Post not found"
            raise PostNotFoundError(msg) from exc

    def get_published_posts_by_category(
        self,
        category: Category,
    ) -> models.QuerySet:
        """Return all published posts for a given category.

        Must have a date less than or equal to the current date/time for a specific
        category, ordered by date in descending order.
        """
        return self.get_published_posts().filter(categories=category)

    # Adjust based on your needs

    def get_published_posts_by_tags(
        self,
        tag_slugs: list[str],
    ) -> models.QuerySet:
        """Return all published posts for a given list of tags.

        Only posts that belong to all the tags in the list should be returned.

        Args:
            tag_slugs (list[str]): A list of the string representations of tags (i.e. slugs).

        Returns:
            models.QuerySet: A queryset of posts that belong to all the tags in the list.
        """
        max_tags_per_query = djpress_settings.MAX_TAGS_PER_QUERY
        if not isinstance(max_tags_per_query, int):  # pragma: no cover
            msg = f"MAX_TAGS_PER_QUERY must be an integer, got {type(max_tags_per_query).__name__}"
            raise TypeError(msg)

        if len(tag_slugs) > max_tags_per_query:
            return self.none()

        # Get all tags first
        tags = Tag.objects.filter(slug__in=tag_slugs)

        # If we didn't find all tags, return empty queryset
        if tags.count() != len(tag_slugs):
            return self.none()

        queryset = self.get_published_posts()
        for tag in tags:
            queryset = queryset.filter(tags=tag)
        return queryset.distinct()

    def get_published_posts_by_author(
        self,
        author: User,
    ) -> models.QuerySet:
        """Return all published posts for a given author.

        Must have a date less than or equal to the current date/time for a specific
        author, ordered by date in descending order.
        """
        return self.get_published_posts().filter(author=author)

    def get_years(self) -> Iterable[datetime.date]:
        """Return a list of years that have published posts.

        Returns:
            Iterable[datetime.date]: A distinct list of dates.
        """
        return self.dates("_date", "year")

    def get_months(self, year: int) -> Iterable[datetime.date]:
        """Return a list of months for a given year that have published posts.

        Args:
            year (int): The year.

        Returns:
            Iterable[datetime.date]: A distinct list of dates.
        """
        return self.filter(_date__year=year).dates("_date", "month")

    def get_days(self, year: int, month: int) -> Iterable[datetime.date]:
        """Return a list of days for a given year and month that have published posts.

        Args:
            year (int): The year.
            month (int): The month.

        Returns:
            Iterable[datetime.date]: A distinct list of dates.
        """
        return self.filter(_date__year=year, _date__month=month).dates("_date", "day")

    def get_year_last_modified(self, year: int) -> timezone.datetime | None:
        """Return the most recent updated_at of posts for a given year.

        Args:
            year (int): The year.

        Returns:
            timezone.datetime | None: The last published post for the given year.
        """
        return self.filter(_date__year=year).aggregate(latest=Max("updated_at"))["latest"]

    def get_month_last_modified(self, year: int, month: int) -> timezone.datetime | None:
        """Return the most recent updated_at of posts for a given month.

        Args:
            year (int): The year.
            month (int): The month.

        Returns:
            timezone.datetime | None: The last published post for the given month.
        """
        return self.filter(_date__year=year, _date__month=month).aggregate(latest=Max("updated_at"))["latest"]

    def get_day_last_modified(self, year: int, month: int, day: int) -> timezone.datetime | None:
        """Return the most recent updated_at of posts for a given day.

        Args:
            year (int): The year.
            month (int): The month.
            day (int): The day.

        Returns:
            timezone.datetime | None: The last published post for the given day.
        """
        return self.filter(_date__year=year, _date__month=month, _date__day=day).aggregate(
            latest=Max("updated_at"),
        )["latest"]


class Post(models.Model):
    """Post model."""

    STATUS_CHOICES = [("draft", "Draft"), ("published", "Published")]
    CONTENT_TYPE_CHOICES = [("post", "Post"), ("page", "Page")]

    # Managers
    objects: PostsAndPagesManager = PostsAndPagesManager()  # Default manager returns only published content
    page_objects: PagesManager = PagesManager()
    post_objects: PostsManager = PostsManager()
    admin_objects: AdminManager = AdminManager()  # Unfiltered - for admin use only

    title = models.CharField(max_length=200, blank=True, help_text="Title is only required for pages.")
    slug = models.SlugField(
        unique=True,
        blank=True,
        help_text=(
            "The slug is automatically generated from the title, or from the first 5 words of the content if no title."
        ),
    )
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    published_at = models.DateTimeField(default=timezone.now)
    _date = models.DateField(
        blank=True,
        null=True,
        help_text="Date that the post was published, without any timezone information. Used for generating the URL.",
    )
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")
    post_type = models.CharField(max_length=10, choices=CONTENT_TYPE_CHOICES, default="post")
    categories = models.ManyToManyField(Category, blank=True, related_name="_posts")
    tags = models.ManyToManyField(Tag, blank=True, related_name="_posts")
    menu_order = models.IntegerField(default=0)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="_children",  # Danger! This returns all children of a parent, published or not.
        limit_choices_to={"post_type": "page"},
    )
    # Type hint for Django's reverse relationship
    if TYPE_CHECKING:
        _children: models.Manager["Post"]

    class Meta:
        """Meta options for the Post model."""

        verbose_name = "post"
        verbose_name_plural = "posts"
        default_manager_name = "admin_objects"  # For Django internals/admin

        permissions = [
            ("can_publish_post", "Can publish post"),
        ]

        indexes = [
            models.Index(fields=["title"], name="djpress_post_title_idx"),
            models.Index(fields=["content"], name="djpress_post_content_idx"),
        ]

    def __str__(self) -> str:
        """Return the string representation of the post."""
        return self.title

    def save(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        """Override the save method."""
        # Generate the slug
        self.slug = self._generate_slug()

        # If the post is a post, we need to ensure that the parent is None
        if self.post_type == "post":
            self.parent = None

        # Generate the _date field from the date field.
        # We only do this if the post is new or if the date has changed. This ensures the _date field doesn't change
        # unless the date field has been specifically changed.
        if self.pk is None:
            self._date = self.published_at.date()
        else:
            old = self.__class__.admin_objects.filter(pk=self.pk).only("published_at").first()
            if old is None or old.published_at != self.published_at:
                self._date = self.local_datetime.date()

        self.full_clean()
        super().save(*args, **kwargs)

        # If the post is a post and it's published, run the post_save_post hook after the transaction is committed
        if self.post_type == "post" and self.is_published:
            on_commit(lambda: registry.run_hook(POST_SAVE_POST, self))

    def clean(self) -> None:
        """Custom validation for the Post model."""
        # Validation for pages
        if self.post_type == "page":
            # Check if the page has a title
            self._check_page_has_title()

            # Check for circular references in the page hierarchy
            self._check_circular_reference()

    def _generate_slug(self) -> str:
        """Generate a slug for the post.

        This is called in the save method if the slug is empty, and must be unique.

        The slug is generated from the title or the first 5 words of the content if the title is empty.

        This does not need to be perfect as the user can always edit the slug in the admin interface.

        Returns:
            str: The generated slug.
        """
        # If the slug is already set, we don't need to do anything
        if self.slug:
            slug = self.slug
        elif self.title:
            # Try generating a slug from the title
            slug = slugify(self.title)
        else:
            # If the title is empty, use the first 5 words of the content
            slug = slugify(" ".join(self.content.split()[:5]))

        # If the slug is empty, raise an error
        if not slug or slug.strip("-") == "":
            msg = "Invalid title. Unable to generate a valid slug."
            raise ValueError(msg)

        return slug

    def _check_page_has_title(self) -> None:
        """Check if the page has a title.

        This is called in the clean method. If the page is a page and it doesn't have a title, we raise a validation
        error.

        Returns:
            None

        Raises:
            ValidationError: If the page doesn't have a title.
        """
        if self.post_type == "page" and not self.title:
            msg = "Page must have a title."
            raise ValidationError(msg)

    def _check_circular_reference(self) -> None:
        """Check for circular references in the page hierarchy.

        This is a recursive function that checks if the current page is an ancestor of itself. This is needed to ensure
        that we don't create a circular reference in the page hierarchy. This is called in the clean method.

        For example, we need to avoid the following page hierarchy from happening:
        - Page A
            - Page B
                - Page C
                    - Page A

        Returns:
            None

        Raises:
            ValidationError: If a circular reference is detected.
        """
        # If there's no parent, we don't need to check for circular references
        if not self.parent:
            return

        ancestor = self.parent
        while ancestor:
            if ancestor.pk == self.pk:
                msg = "Circular reference detected in page hierarchy."
                raise ValidationError(msg)
            ancestor = ancestor.parent

    @property
    def children(self) -> models.QuerySet:
        """Return only published children pages."""
        return self._children.filter(
            status="published",
            published_at__lte=timezone.now(),
        ).order_by("menu_order", "title")

    @property
    def content_markdown(self) -> str:
        """Return the content as HTML converted from Markdown."""
        # Get the raw markdown content
        content = self.content

        # Let plugins modify the markdown before rendering
        content = registry.run_hook(PRE_RENDER_CONTENT, content)

        # Render the markdown
        html_content = render_markdown(content)

        # Let the plugins modify the markdown after rendering and return the results
        return str(registry.run_hook(POST_RENDER_CONTENT, html_content) or "")

    @property
    def truncated_content_markdown(self) -> str:
        """Return the truncated content as HTML converted from Markdown."""
        truncate_tag = djpress_settings.TRUNCATE_TAG
        if not isinstance(truncate_tag, str) or not truncate_tag:  # pragma: no cover
            msg = "TRUNCATE_TAG must be a non-empty string."
            raise ValueError(msg)
        read_more_index = self.content.find(truncate_tag)
        truncated_content = self.content[:read_more_index] if read_more_index != -1 else self.content
        return render_markdown(truncated_content)

    @property
    def is_truncated(self) -> bool:
        """Return whether the content is truncated."""
        truncate_tag = djpress_settings.TRUNCATE_TAG
        if not isinstance(truncate_tag, str) or not truncate_tag:  # pragma: no cover
            msg = "TRUNCATE_TAG must be a non-empty string."
            raise ValueError(msg)
        return truncate_tag in self.content

    @property
    def url(self) -> str:
        """Return the post's URL.

        Returns:
            str: The post's URL.
        """
        # Avoid circular import
        from djpress.url_utils import get_page_url, get_post_url

        if self.post_type == "page":
            return get_page_url(self)

        return get_post_url(self)

    @property
    def full_page_path(self) -> str:
        """Return the full page path.

        This is the full path to the page, including any parent pages.

        Returns:
            str: The full page path.
        """
        if self.parent:
            return f"{self.parent.full_page_path}/{self.slug}"
        return self.slug

    @property
    def is_published(self) -> bool:
        """Return whether the post or page is published.

        For a post to be published, it must meet the following requirements:
        - The status must be "published".
        - The date must be less than or equal to the current date/time.

        For a page to be published, it must meet the following requirements:
        - The status must be "published".
        - The date must be less than or equal to the current date/time.
        - All ancestor pages must also be published.

        Returns:
            bool: Whether the post is published.
        """
        # If the post or page status is not published or the date is in the future, return False
        if not (self.status == "published" and self.published_at <= timezone.now()):
            return False

        # If the post is a page and has a parent, check if the parent is published
        if self.post_type == "page" and self.parent:
            return self.parent.is_published

        # If we get to here, the post is published
        return True

    @property
    def is_parent(self) -> bool:
        """Return whether the post is a parent page.

        Returns:
            bool: Whether the post is a parent page.
        """
        return self.children.exists()

    @property
    def is_child(self) -> bool:
        """Return whether the post is a child page.

        Returns:
            bool: Whether the post is a child page.
        """
        return self.parent is not None

    @property
    def post_title(self) -> str:
        """Return the post title.

        This is used to display the post title in the admin interface. If the post is a page, we return the page title.
        If the post is a post, we return the post title or create a title from the slug if there's no title.

        See the `_generate_slug` method for more details on how the slug is generated.

        If the resulting title looks odd due to how the slug has been generated, the user can always edit the slug in
        the admin interface which will update the title.

        Returns:
            str: The post title.
        """
        if self.post_type == "page":
            return self.title

        if not self.title:
            # Get the title from the slug and replace hyphens with spaces
            title = self.slug.replace("-", " ").capitalize()  # Capitalize the first letter

            return f"{title}..."

        return self.title

    @property
    def local_datetime(self) -> timezone.datetime:
        """Return the post date in the local timezone.

        This is used to get the date of the post in the `TIME_ZONE` that is configured in `settings.py`.

        Returns:
            timezone.datetime: The post date in the local timezone.
        """
        return timezone.localtime(self.published_at)
