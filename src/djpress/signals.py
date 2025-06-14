"""Signals for djpress app."""

from django.apps import AppConfig
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db.models.signals import post_delete, post_migrate, post_save
from django.dispatch import receiver

from djpress.models import Media
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


@receiver(post_migrate)
def create_groups(sender: AppConfig, **_) -> None:  # noqa: ANN003
    """Create groups and assign permissions."""
    if sender.name != "djpress":
        return

    # Get content types
    post_content_type = ContentType.objects.get_for_model(Post)
    category_content_type = ContentType.objects.get_for_model(Category)

    # Get permissions
    standard_permissions = Permission.objects.filter(
        content_type=post_content_type,
        codename__in=["add_post", "change_post", "delete_post"],
    )
    publish_permission = Permission.objects.get(
        content_type=post_content_type,
        codename="can_publish_post",
    )
    category_permissions = Permission.objects.filter(
        content_type=category_content_type,
        codename__in=["add_category", "change_category", "delete_category"],
    )
    tag_permissions = Permission.objects.filter(
        content_type=ContentType.objects.get_for_model(Tag),
        codename__in=["add_tag", "change_tag", "delete_tag"],
    )
    tag_add_permission = Permission.objects.get(
        content_type=ContentType.objects.get_for_model(Tag),
        codename="add_tag",
    )
    media_permissions = Permission.objects.filter(
        content_type=ContentType.objects.get_for_model(Media),
        codename__in=["add_media", "change_media", "delete_media"],
    )

    # Create groups and assign permissions
    editor_group, _ = Group.objects.get_or_create(name="editor")
    editor_group.permissions.add(
        publish_permission,
        *standard_permissions,
        *category_permissions,
        *tag_permissions,
        *media_permissions,
    )

    author_group, _ = Group.objects.get_or_create(name="author")
    author_group.permissions.add(publish_permission, *standard_permissions, tag_add_permission, *media_permissions)

    contributor_group, _ = Group.objects.get_or_create(name="contributor")
    contributor_group.permissions.add(*standard_permissions, tag_add_permission, *media_permissions)


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
