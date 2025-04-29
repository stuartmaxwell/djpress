"""Tag model."""

from django.core.cache import cache
from django.db import IntegrityError, models, transaction
from django.db.models import Max
from django.utils import timezone
from django.utils.text import slugify

from djpress.conf import settings as djpress_settings

TAG_CACHE_KEY = "tags"


class TagManager(models.Manager):
    """Tag manager."""

    def get_queryset(self) -> models.QuerySet:
        """Return the default queryset for tag."""
        return super().get_queryset()

    def get_tags(self) -> models.QuerySet:
        """Return the queryset for tags.

        This should be used instead of the default queryset to get the tags since it will check the cache first if
        needed.

        If CACHE_TAGS is set to True, we return the cached queryset. Or if there's no cached queryset, we cache it
        and then return it.
        """
        if djpress_settings.CACHE_TAGS:
            return self._get_cached_tags()

        return self.get_queryset()

    def _get_cached_tags(self) -> models.QuerySet:
        """Return the cached tags queryset."""
        queryset = cache.get(TAG_CACHE_KEY)

        if queryset is None:
            queryset = self.get_queryset()
            cache.set(TAG_CACHE_KEY, queryset, timeout=None)

        return queryset

    def get_tag_by_slug(self, slug: str) -> "Tag":
        """Return a single tag by its slug.

        If tag caching is enabled, we first try to get the tag from the cache. If the tag is not found in the cache,
        we fetch it from the database.

        Args:
            slug (str): The slug of the tag.

        Returns:
            Tag: The tag with the given slug.

        Raises:
            ValueError: If the tag is not found.
        """
        tags = self.get_tags()
        tag = next(
            (tag for tag in tags if tag.slug == slug),
            None,
        )

        # If no tag is found, either it doesn't exist, or if caching is enabled, it's not in the cache.
        if not tag:
            # If caching is not enabled, we raise a ValueError.
            if not djpress_settings.CACHE_TAGS:
                msg = "Tag not found"
                raise ValueError(msg)

            # If caching is enabled, we try fetch the tag from the database.
            try:
                tag = self.get(slug=slug)
            except Tag.DoesNotExist as exc:
                msg = "Tag not found"
                # Raise a 404 error
                raise ValueError(msg) from exc

        return tag

    def get_tags_with_published_posts(self) -> models.QuerySet:
        """Return a queryset of tags that have published posts.

        We can use the has_posts property to include only tags with published posts.
        """
        return Tag.objects.filter(pk__in=[tag.pk for tag in self.get_queryset() if tag.has_posts])


class Tag(models.Model):
    """Tag model."""

    # Manager
    objects: TagManager = TagManager()

    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        """Meta options for the tag model."""

        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self) -> str:
        """Return the title of the tag."""
        return self.title

    def save(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        """Override the save method to auto-generate the slug."""
        if not self.slug:
            self.slug = slugify(self.title)
            if not self.slug or self.slug.strip("-") == "":
                msg = "Invalid title. Unable to generate a valid slug."
                raise ValueError(msg)

        try:
            with transaction.atomic():
                super().save(*args, **kwargs)
        except IntegrityError as exc:
            msg = f"A tag with the slug {self.slug} already exists."
            raise ValueError(msg) from exc

    @property
    def url(self) -> str:
        """Return the tag's URL."""
        from djpress.url_utils import get_tag_url

        return get_tag_url(self)

    @property
    def posts(self) -> models.QuerySet:
        """Return only published posts.

        Note: this mirrors the queryset in PostsManager.
        """
        return self._posts.filter(
            post_type="post",
            status="published",
            date__lte=timezone.now(),
        ).order_by("-date")

    @property
    def has_posts(self) -> bool:
        """Return True if the tag has published posts."""
        return self.posts.exists()

    @property
    def last_modified(self) -> None | timezone.datetime:
        """Return the most recent last modified date of posts in the tag.

        This property is used in the sitemap to determine the last modified date of the tag.

        If the tag has no published posts, we return None.

        Returns:
            None | timezone.datetime: The most recent last modified date of posts in the tag.
        """
        return self.posts.aggregate(latest=Max("modified_date"))["latest"]
