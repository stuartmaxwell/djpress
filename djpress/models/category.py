"""Category model."""

from django.conf import settings
from django.core.cache import cache
from django.db import IntegrityError, models, transaction
from django.utils.text import slugify

CATEGORY_CACHE_KEY = "categories"


class CategoryManager(models.Manager):
    """Category manager."""

    def get_categories(self: "CategoryManager") -> models.QuerySet:
        """Return the queryset for categories.

        If CACHE_CATEGORIES is set to True, we return the cached queryset.
        """
        if settings.CACHE_CATEGORIES:
            return self._get_cached_categories()

        return self.all()

    def _get_cached_categories(self: "CategoryManager") -> models.QuerySet:
        """Return the cached categories queryset."""
        queryset = cache.get(CATEGORY_CACHE_KEY)

        if queryset is None:
            queryset = self.all()
            cache.set(CATEGORY_CACHE_KEY, queryset, timeout=None)

        return queryset

    def get_category_by_slug(self: "CategoryManager", slug: str) -> "Category":
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


class Category(models.Model):
    """Category model."""

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)

    # Custom Manager
    objects: "CategoryManager" = CategoryManager()

    class Meta:
        """Meta options for the category model."""

        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self: "Category") -> str:
        """Return the string representation of the category."""
        return self.name

    def save(self: "Category", *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        """Override the save method to auto-generate the slug."""
        if not self.slug:
            self.slug = slugify(self.name)
            if not self.slug or self.slug.strip("-") == "":
                msg = "Invalid name. Unable to generate a valid slug."
                raise ValueError(msg)

        try:
            with transaction.atomic():
                super().save(*args, **kwargs)
        except IntegrityError as exc:
            msg = f"A category with the slug {self.slug} already exists."
            raise ValueError(msg) from exc

    @property
    def permalink(self: "Category") -> str:
        """Return the category's permalink."""
        if settings.CATEGORY_PATH_ENABLED and settings.CATEGORY_PATH:
            return f"{settings.CATEGORY_PATH}/{self.slug}"

        return f"{self.slug}"
