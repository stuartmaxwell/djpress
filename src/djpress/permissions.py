"""Permissions and group management for djpress app."""

import logging

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import OperationalError, ProgrammingError

from djpress.models import Category, Media, PluginStorage, Post, Tag

logger = logging.getLogger(__name__)


def create_groups() -> None:
    """Create groups and assign permissions.

    Creates four groups with different permission levels:
    - djpress_admin: Full permissions to all djpress models
    - djpress_editor: Can publish posts and manage all content
    - djpress_author: Can publish their own posts and add tags/media
    - djpress_contributor: Can create/edit posts (but not publish) and add tags/media

    This function is idempotent and safe to run multiple times.
    """
    try:
        # Get content types for all models
        post_content_type = ContentType.objects.get_for_model(Post)
        category_content_type = ContentType.objects.get_for_model(Category)
        tag_content_type = ContentType.objects.get_for_model(Tag)
        media_content_type = ContentType.objects.get_for_model(Media)
        plugin_storage_content_type = ContentType.objects.get_for_model(PluginStorage)

        # Get all permissions for admin group
        all_post_permissions = Permission.objects.filter(content_type=post_content_type)
        all_category_permissions = Permission.objects.filter(content_type=category_content_type)
        all_tag_permissions = Permission.objects.filter(content_type=tag_content_type)
        all_media_permissions = Permission.objects.filter(content_type=media_content_type)
        all_plugin_storage_permissions = Permission.objects.filter(content_type=plugin_storage_content_type)

        # Get specific permissions for other groups
        post_permissions = Permission.objects.filter(
            content_type=post_content_type,
            codename__in=["add_post", "change_post", "delete_post"],
        )
        post_add_change_permissions = Permission.objects.filter(
            content_type=post_content_type,
            codename__in=["add_post", "change_post"],
        )
        publish_permissions = Permission.objects.filter(
            content_type=post_content_type,
            codename__in=["can_publish_post"],
        )
        category_permissions = Permission.objects.filter(
            content_type=category_content_type,
            codename__in=["add_category", "change_category", "delete_category"],
        )
        category_view_permissions = Permission.objects.filter(
            content_type=category_content_type,
            codename__in=["view_category"],
        )
        tag_permissions = Permission.objects.filter(
            content_type=tag_content_type,
            codename__in=["add_tag", "change_tag", "delete_tag"],
        )
        tag_add_permissions = Permission.objects.filter(
            content_type=tag_content_type,
            codename__in=["add_tag", "view_tag"],
        )
        media_permissions = Permission.objects.filter(
            content_type=media_content_type,
            codename__in=["add_media", "change_media", "delete_media"],
        )
        media_add_change_permissions = Permission.objects.filter(
            content_type=media_content_type,
            codename__in=["add_media", "change_media"],
        )
        media_add_permissions = Permission.objects.filter(
            content_type=media_content_type,
            codename__in=["add_media", "view_media"],
        )

        # Create admin group with full permissions
        admin_group, created = Group.objects.get_or_create(name="djpress_admin")
        if created:
            logger.info("Created 'djpress_admin' group")
        admin_group.permissions.set(
            [
                *all_post_permissions,
                *all_category_permissions,
                *all_tag_permissions,
                *all_media_permissions,
                *all_plugin_storage_permissions,
            ]
        )

        # Create editor group
        editor_group, created = Group.objects.get_or_create(name="djpress_editor")
        if created:
            logger.info("Created 'djpress_editor' group")
        editor_group.permissions.set(
            [
                *publish_permissions,
                *post_permissions,
                *category_permissions,
                *tag_permissions,
                *media_permissions,
            ]
        )

        # Create author group
        author_group, created = Group.objects.get_or_create(name="djpress_author")
        if created:
            logger.info("Created 'djpress_author' group")
        author_group.permissions.set(
            [
                *publish_permissions,
                *post_add_change_permissions,
                *tag_add_permissions,
                *media_add_change_permissions,
            ]
        )

        # Create contributor group
        contributor_group, created = Group.objects.get_or_create(name="djpress_contributor")
        if created:
            logger.info("Created 'djpress_contributor' group")
        contributor_group.permissions.set(
            [
                *post_add_change_permissions,
                *tag_add_permissions,
                *media_add_permissions,
                *category_view_permissions,
            ]
        )

        logger.info("Successfully configured DJ Press groups and permissions")

    except (OperationalError, ProgrammingError) as e:
        # Database tables don't exist yet (migrations haven't run)
        logger.debug(f"Cannot create groups yet - database not ready: {e}")
    except ObjectDoesNotExist as e:
        # ContentType or Permission doesn't exist yet
        logger.debug(f"Cannot create groups yet - models not ready: {e}")
    except Exception:
        # Catch any other unexpected errors
        logger.exception("Unexpected error creating groups.")
