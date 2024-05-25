"""Signals for djpress app."""

from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from djpress.models.category import (
    CATEGORY_CACHE_KEY,
    Category,
)
from djpress.models.post import (
    PUBLISHED_POSTS_CACHE_KEY,
    Post,
)


@receiver(post_save, sender=Category)
@receiver(post_delete, sender=Category)
def invalidate_category_cache(**kwargs) -> None:  # noqa: ARG001, ANN003
    """Invalidate the category cache."""
    cache.delete(CATEGORY_CACHE_KEY)


@receiver(post_save, sender=Post)
@receiver(post_delete, sender=Post)
def invalidate_published_content_cache(**kwargs) -> None:  # noqa: ARG001, ANN003
    """Invalidate the published posts cache."""
    cache.delete(PUBLISHED_POSTS_CACHE_KEY)
