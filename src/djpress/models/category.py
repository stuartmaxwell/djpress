"""Category model."""

from typing import TYPE_CHECKING

from django.core.cache import cache
from django.db import IntegrityError, models, transaction
from django.db.models import Max
from django.utils import timezone
from django.utils.text import slugify

from djpress.conf import settings as djpress_settings

CATEGORY_CACHE_KEY = "categories"


class CategoryManager(models.Manager):
    """Category manager."""

    def get_categories(self) -> models.QuerySet:
        """Return the queryset for categories.

        If CACHE_CATEGORIES is set to True, we return the cached queryset.
        """
        if djpress_settings.CACHE_CATEGORIES:
            return self._get_cached_categories()

        return self.all()

    def _get_cached_categories(self) -> models.QuerySet:
        """Return the cached categories queryset."""
        queryset = cache.get(CATEGORY_CACHE_KEY)

        if queryset is None:
            queryset = self.all()
            cache.set(CATEGORY_CACHE_KEY, queryset, timeout=None)

        return queryset

    def get_category_by_slug(self, slug: str) -> "Category":
        """Return a single category by its slug."""
        # First, try to get the category from the cache
        categories = self.get_categories()
        category = next(
            (category for category in categories if category.slug == slug),
            None,
        )

        # If the category is not found in the cache, fetch it from the database
        if not category:
            try:
                category = self.get(slug=slug)
            except Category.DoesNotExist as exc:
                msg = "Category not found"
                # Raise a 404 error
                raise ValueError(msg) from exc

        return category

    def get_categories_with_published_posts(self) -> models.QuerySet:
        """Return a queryset of categories that have published posts.

        We can use the has_posts property to include only categories with published posts.
        """
        return Category.objects.filter(pk__in=[category.pk for category in self.get_queryset() if category.has_posts])


class Category(models.Model):
    """Category model."""

    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    menu_order = models.IntegerField(default=0)
    # Type hint for Django's reverse relationship
    if TYPE_CHECKING:
        from djpress.models.post import Post

        _posts: models.Manager["Post"]

    # Custom Manager
    objects: "CategoryManager" = CategoryManager()

    class Meta:
        """Meta options for the category model."""

        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self) -> str:
        """Return the string representation of the category."""
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
            msg = f"A category with the slug {self.slug} already exists."
            raise ValueError(msg) from exc

    @property
    def url(self) -> str:
        """Return the category's URL."""
        from djpress.url_utils import get_category_url

        return get_category_url(self)

    @property
    def posts(self: "Category") -> models.QuerySet:
        """Return only published posts.

        Note: this mirrors the queryset in PostsManager.
        """
        return self._posts.filter(
            post_type="post",
            status="published",
            published_at__lte=timezone.now(),
        ).order_by("-published_at")

    @property
    def has_posts(self) -> bool:
        """Return True if the category has published posts."""
        return self.posts.exists()

    @property
    def last_modified(self) -> None | timezone.datetime:
        """Return the most recent last modified date of posts in the category.

        This property is used in the sitemap to determine the last modified date of the category.

        If the category has no published posts, we return None.

        Returns:
            None | timezone.datetime: The most recent last modified date of posts in the category.
        """
        return self.posts.aggregate(latest=Max("updated_at"))["latest"]
