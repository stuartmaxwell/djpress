"""Signals for djpress app."""

from django.apps import AppConfig
from django.core.cache import cache
from django.core.signals import request_started
from django.db.models.signals import post_delete, post_migrate, post_save
from django.dispatch import receiver

from djpress.conf import settings as djpress_settings
from djpress.models.category import (
    CATEGORY_CACHE_KEY,
    Category,
)
from djpress.models.post import (
    PUBLISHED_POSTS_CACHE_KEY,
    Post,
)
from djpress.models.setting import (
    SETTING_CACHE_KEY,
    Setting,
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


@receiver(post_save, sender=Setting)
@receiver(post_delete, sender=Setting)
def invalidate_setting_cache(**_) -> None:  # noqa: ANN003
    """Invalidate the settings cache.

    We invalidate the cache when a setting is saved or deleted.
    """
    cache.delete(SETTING_CACHE_KEY)
    djpress_settings.clear_request_cache()


@receiver(request_started)
def clear_settings_request_cache(**_) -> None:  # noqa: ANN003
    """Clear the local request-bound settings cache at the start of each request."""
    djpress_settings.clear_request_cache()
