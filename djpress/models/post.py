"""Post model."""

import logging
from typing import ClassVar

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from djpress.models import Category
from djpress.utils import render_markdown

logger = logging.getLogger(__name__)


PUBLISHED_POSTS_CACHE_KEY = "published_posts"


class PostsManager(models.Manager):
    """Post custom manager."""

    def get_queryset(self: "PostsManager") -> models.QuerySet:
        """Return the queryset for published posts."""
        return super().get_queryset().filter(post_type="post").order_by("-date")

    def _get_published_posts(self: "PostsManager") -> models.QuerySet:
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

        If CACHE_RECENT_PUBLISHED_POSTS is set to True, we return the cached queryset.
        """
        if settings.CACHE_RECENT_PUBLISHED_POSTS:
            return self._get_cached_recent_published_posts()

        return self._get_published_posts().prefetch_related("categories", "author")[
            : settings.RECENT_PUBLISHED_POSTS_COUNT
        ]

    def _get_cached_recent_published_posts(self: "PostsManager") -> models.QuerySet:
        """Return the cached recent published posts queryset.

        If there are any future posts, we calculate the seconds until that post, then we
        set the timeout to that number of seconds.
        """
        queryset = cache.get(PUBLISHED_POSTS_CACHE_KEY)

        if queryset is None:
            queryset = (
                self.get_queryset()
                .filter(
                    status="published",
                )
                .prefetch_related("categories", "author")
            )

            future_posts = queryset.filter(date__gt=timezone.now())
            if future_posts.exists():
                future_post = future_posts[0]
                timeout = (future_post.date - timezone.now()).total_seconds()
            else:
                timeout = None

            queryset = queryset.filter(date__lte=timezone.now())[
                : settings.RECENT_PUBLISHED_POSTS_COUNT
            ]
            cache.set(
                PUBLISHED_POSTS_CACHE_KEY,
                queryset,
                timeout=timeout,
            )

        return queryset

    def get_published_post_by_slug(
        self: "PostsManager",
        slug: str,
    ) -> "Post":
        """Return a single published post.

        Must have a date less than or equal to the current date/time based on its slug.
        """
        # First, try to get the post from the cache
        posts = self.get_recent_published_posts()
        post = next((post for post in posts if post.slug == slug), None)

        # If the post is not found in the cache, fetch it from the database
        if not post:
            try:
                post = self._get_published_posts().get(slug=slug)
            except Post.DoesNotExist as exc:
                msg = "Post not found"
                raise ValueError(msg) from exc

        return post

    def get_published_post_by_path(
        self: "PostsManager",
        path: str,
    ) -> "Post":
        """Return a single published post from a path.

        This is a complex piece of logic...

        Here are all the different valid paths that we need to check:
        - /blog/2021/01/01/post-slug
        - /blog/2021/01/post-slug
        - /blog/2021/post-slug
        - /blog/post-slug
        - /2021/01/01/post-slug
        - /2021/01/post-slug
        - /2021/post-slug
        - /post-slug

        But we could be getting any invalid path too, e.g.
        - /blog/2021/01/01/post-slug/extra
        - /blog/2021/01/post-slug/extra
        - etc.

        This is what we need to do...

        First, we need to know the following:
        - Is there a POST_PREFIX defined?
        - Are DATE_ARCHIVES enabled?
        - If DATE_ARCHIVES are enabled, what is the POST_PERMALINK set to?

        I don't think I can avoid regex matching here...

        For now we'll just look at the POST_PREFIX.
        """
        if settings.POST_PREFIX and path.startswith(settings.POST_PREFIX):
            slug = path.split(settings.POST_PREFIX + "/")[1]
            return self.get_published_post_by_slug(slug)

        if settings.POST_PREFIX and not path.startswith(settings.POST_PREFIX):
            msg = "Invalid path"
            raise ValueError(msg)

        return self.get_published_post_by_slug(path)

    def get_published_posts_by_category(
        self: "PostsManager",
        category: Category,
    ) -> models.QuerySet:
        """Return all published posts for a given category.

        Must have a date less than or equal to the current date/time for a specific
        category, ordered by date in descending order.
        """
        return (
            self._get_published_posts()
            .filter(categories=category)
            .prefetch_related("categories", "author")
        )

    def get_published_posts_by_author(
        self: "PostsManager",
        author: User,
    ) -> models.QuerySet:
        """Return all published posts for a given author.

        Must have a date less than or equal to the current date/time for a specific
        author, ordered by date in descending order.
        """
        return (
            self._get_published_posts()
            .filter(author=author)
            .prefetch_related("categories", "author")
        )


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
    post_type = models.CharField(
        max_length=10,
        choices=CONTENT_TYPE_CHOICES,
        default="post",
    )
    categories = models.ManyToManyField(Category, blank=True)

    # Managers
    objects = models.Manager()
    post_objects: "PostsManager" = PostsManager()

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
        super().save(*args, **kwargs)

    @property
    def content_markdown(self: "Post") -> str:
        """Return the content as HTML converted from Markdown."""
        return render_markdown(self.content)

    @property
    def truncated_content_markdown(self: "Post") -> str:
        """Return the truncated content as HTML converted from Markdown."""
        read_more_index = self.content.find(settings.TRUNCATE_TAG)
        if read_more_index != -1:
            truncated_content = self.content[:read_more_index]
        else:
            truncated_content = self.content
        return render_markdown(truncated_content)

    @property
    def is_truncated(self: "Post") -> bool:
        """Return whether the content is truncated."""
        return settings.TRUNCATE_TAG in self.content

    @property
    def permalink(self: "Post") -> str:
        """Return the post's permalink.

        The posts permalink is constructed of the following elements:
        - The post prefix - this is configured in POST_PREFIX and could be an empty
          string or a custom string, e.g. `blog` or `posts`.
        - The post date structure - this is configured in POST_PERMALINK and is a
          `strftime` value, e.g. `%Y/%m/%d` or `%Y/%m`. Or it could be an empty string
          to indicate that no date structure is used.
        - The post slug - this is a unique identifier for the post. TODO: should this be
          a database unique constraint, or should we handle it in software instead?
        """
        # We start the permalink with just the slug
        permalink = self.slug

        # If the post type is a page, we return just the slug
        if self.post_type == "page":
            return permalink

        # The only other post type is a post so we don't need to check for that
        # If there's a permalink structure defined, we add that to the permalink
        if settings.POST_PERMALINK:
            permalink = f"{self.date.strftime(settings.POST_PERMALINK)}/{self.slug}"

        # If there's a post prefix defined, we add that to the permalink
        if settings.POST_PREFIX:
            permalink = f"{settings.POST_PREFIX}/{permalink}"

        return permalink
