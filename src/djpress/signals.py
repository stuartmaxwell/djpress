"""Signals for djpress app."""

from django.apps import AppConfig
from django.core.cache import cache
from django.db.models.signals import post_delete, post_migrate, post_save
from django.dispatch import receiver

from djpress.models.category import (
    CATEGORY_CACHE_KEY,
    Category,
)
from djpress.models.post import (
    PUBLISHED_POSTS_CACHE_KEY,
    Post,
)
from djpress.models.tag import (
    TAG_CACHE_KEY,
    Tag,
)
from djpress.permissions import create_groups as setup_groups


@receiver(post_migrate)
def create_groups(sender: AppConfig, **_) -> None:  # noqa: ANN003
    """Create groups and assign permissions after migrations."""
    if sender.name != "djpress":
        return

    setup_groups()


@receiver(post_save, sender=Category)
@receiver(post_delete, sender=Category)
def invalidate_category_cache(**_) -> None:  # noqa: ANN003
    """Invalidate the category cache.

    We invalidate the cache when a category is saved or deleted.
    """
    cache.delete(CATEGORY_CACHE_KEY)


@receiver(post_save, sender=Post)
@receiver(post_delete, sender=Post)
def invalidate_published_content_cache(**_) -> None:  # noqa: ANN003
    """Invalidate the published posts cache.

    We invalidate the cache when a post is saved or deleted.
    """
    cache.delete(PUBLISHED_POSTS_CACHE_KEY)


@receiver(post_save, sender=Tag)
@receiver(post_delete, sender=Tag)
def invalidate_tag_cache(**_) -> None:  # noqa: ANN003
    """Invalidate the tag cache.

    We invalidate the cache when a tag is saved or deleted.
    """
    cache.delete(TAG_CACHE_KEY)
