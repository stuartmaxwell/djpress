"""Post model."""

import logging
from typing import ClassVar

from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from djpress.conf import settings as djpress_settings
from djpress.exceptions import PageNotFoundError, PostNotFoundError
from djpress.models import Category
from djpress.utils import render_markdown

logger = logging.getLogger(__name__)


PUBLISHED_POSTS_CACHE_KEY = "published_posts"


class PagesManager(models.Manager):
    """Page custom manager."""

    def get_queryset(self: "PagesManager") -> models.QuerySet:
        """Return the queryset for pages."""
        return super().get_queryset().filter(post_type="page").order_by("-date")

    def get_published_pages(self: "PagesManager") -> models.QuerySet:
        """Return all published pages.

        For a page to be considered published, it must meet the following requirements:
        - The status must be "published".
        - The date must be less than or equal to the current date/time.
        """
        return self.get_queryset().filter(
            status="published",
            date__lte=timezone.now(),
        )

    def get_published_page_by_slug(
        self: "PagesManager",
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
        self: "PagesManager",
        path: str,
    ) -> "Post":
        """Return a single published page from a path.

        For now, we'll only allow a top level path.

        This will raise a ValueError if the path is invalid.
        """
        # Check for a single item in the path
        if path.count("/") > 0:
            msg = "Invalid path"
            raise ValueError(msg)

        return self.get_published_page_by_slug(path)


class PostsManager(models.Manager):
    """Post custom manager."""

    def get_queryset(self: "PostsManager") -> models.QuerySet:
        """Return the queryset for posts."""
        return super().get_queryset().filter(post_type="post").order_by("-date")

    def get_published_posts(self: "PostsManager") -> models.QuerySet:
        """Returns all published posts.

        For a post to be considered published, it must meet the following requirements:
        - The status must be "published".
        - The date must be less than or equal to the current date/time.
        """
        return self.get_queryset().filter(
            status="published",
            date__lte=timezone.now(),
        )

    def get_recent_published_posts(self: "PostsManager") -> models.QuerySet:
        """Return recent published posts.

        This does not return a paginated queryset. Use get_paginated_published_posts
        instead.

        If CACHE_RECENT_PUBLISHED_POSTS is set to True, we return the cached queryset.
        """
        if djpress_settings.CACHE_RECENT_PUBLISHED_POSTS:
            return self._get_cached_recent_published_posts()

        return self.get_published_posts().prefetch_related("categories", "author")[
            : djpress_settings.RECENT_PUBLISHED_POSTS_COUNT
        ]

    def _get_cached_recent_published_posts(self: "PostsManager") -> models.QuerySet:
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
            queryset = self.get_queryset().filter(status="published").prefetch_related("categories", "author")
            timeout = self._get_cache_timeout(queryset)
            queryset = queryset.filter(date__lte=timezone.now())[: djpress_settings.RECENT_PUBLISHED_POSTS_COUNT]

            cache.set(
                PUBLISHED_POSTS_CACHE_KEY,
                queryset,
                timeout=timeout,
            )

        return queryset

    def _get_cache_timeout(
        self: "PostsManager",
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
        future_posts = queryset.filter(date__gt=timezone.now())
        if future_posts.exists():
            future_post = future_posts[0]
            return (future_post.date - timezone.now()).total_seconds()

        return None

    def get_published_post_by_slug(
        self: "PostsManager",
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
            filters["date__year"] = year

        if month:
            filters["date__month"] = month

        if day:
            filters["date__day"] = day

        try:
            return self.get_published_posts().get(**filters)
        except Post.DoesNotExist as exc:
            msg = "Post not found"
            raise PostNotFoundError(msg) from exc

    def get_published_posts_by_category(
        self: "PostsManager",
        category: Category,
    ) -> models.QuerySet:
        """Return all published posts for a given category.

        Must have a date less than or equal to the current date/time for a specific
        category, ordered by date in descending order.
        """
        return self.get_published_posts().filter(categories=category).prefetch_related("categories", "author")

    def get_published_posts_by_author(
        self: "PostsManager",
        author: User,
    ) -> models.QuerySet:
        """Return all published posts for a given author.

        Must have a date less than or equal to the current date/time for a specific
        author, ordered by date in descending order.
        """
        return self.get_published_posts().filter(author=author).prefetch_related("categories", "author")


class Post(models.Model):
    """Post model."""

    STATUS_CHOICES: ClassVar = [("draft", "Draft"), ("published", "Published")]
    CONTENT_TYPE_CHOICES: ClassVar = [("post", "Post"), ("page", "Page")]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")
    post_type = models.CharField(max_length=10, choices=CONTENT_TYPE_CHOICES, default="post")
    categories = models.ManyToManyField(Category, blank=True)
    menu_order = models.IntegerField(default=0)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
        limit_choices_to={"post_type": "page"},
    )

    # Managers
    objects = models.Manager()
    post_objects: "PostsManager" = PostsManager()
    page_objects: "PagesManager" = PagesManager()

    class Meta:
        """Meta options for the Post model."""

        verbose_name = "post"
        verbose_name_plural = "posts"

    def __str__(self: "Post") -> str:
        """Return the string representation of the post."""
        return self.title

    def save(self: "Post", *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        """Override the save method to auto-generate the slug."""
        if not self.slug:
            self.slug = slugify(self.title)
            if not self.slug or self.slug.strip("-") == "":
                msg = "Invalid title. Unable to generate a valid slug."
                raise ValueError(msg)
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self) -> None:
        """Custom validation for the Post model."""
        # Check for circular references in the page hierarchy
        self._check_circular_reference()

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
    def content_markdown(self: "Post") -> str:
        """Return the content as HTML converted from Markdown."""
        return render_markdown(self.content)

    @property
    def truncated_content_markdown(self: "Post") -> str:
        """Return the truncated content as HTML converted from Markdown."""
        read_more_index = self.content.find(djpress_settings.TRUNCATE_TAG)
        truncated_content = self.content[:read_more_index] if read_more_index != -1 else self.content
        return render_markdown(truncated_content)

    @property
    def is_truncated(self: "Post") -> bool:
        """Return whether the content is truncated."""
        return djpress_settings.TRUNCATE_TAG in self.content

    @property
    def url(self: "Post") -> str:
        """Return the post's URL.

        Returns:
            str: The post's URL.
        """
        from djpress.url_utils import get_page_url, get_post_url

        if self.post_type == "page":
            return get_page_url(self)

        return get_post_url(self)

    @property
    def permalink(self: "Post") -> str:
        """Return the post's permalink.

        The posts permalink is constructed of the following elements:
        - The post prefix - this is configured in POST_PREFIX and could be an empty
          string or a custom string.
        - The post slug - this is a unique identifier for the post. TODO: should this be
          a database unique constraint, or should we handle it in software instead?
        """
        # If the post type is a page, we return just the slug
        # TODO: needs to support parent pages
        if self.post_type == "page":
            return self.slug

        prefix = djpress_settings.POST_PREFIX

        # Replace placeholders in POST_PREFIX with actual values
        replacements = {
            "{{ year }}": self.date.strftime("%Y"),
            "{{ month }}": self.date.strftime("%m"),
            "{{ day }}": self.date.strftime("%d"),
        }

        for placeholder, value in replacements.items():
            prefix = prefix.replace(placeholder, value)

        # Ensure there's no leading or trailing slash, then join with the slug
        url_parts = [part for part in prefix.split("/") if part] + [self.slug]

        return "/".join(url_parts)

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
