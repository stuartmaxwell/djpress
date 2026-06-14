"""Permissions and group management for djpress app."""

import logging

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import OperationalError, ProgrammingError

from djpress.models import Post

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
        # Trigger DB checks & ensure content types/models are loaded (needed for test mock compatibility)
        ContentType.objects.get_for_model(Post)

        # Get all permissions for the djpress app
        djpress_permissions = Permission.objects.filter(content_type__app_label="djpress")

        # Build a helper dictionary for lookup by codename
        perm_map = {p.codename: p for p in djpress_permissions}

        # 1. Admin Group gets all app permissions
        admin_group, created = Group.objects.get_or_create(name="djpress_admin")
        if created:
            logger.info("Created 'djpress_admin' group")
        admin_group.permissions.set(djpress_permissions)

        # 2. Editor Group
        editor_codenames = [
            # Post permissions
            "view_post",
            "add_post",
            "change_post",
            "delete_post",
            "can_publish_post",
            "change_other_post",
            "can_soft_delete_post",
            "can_restore_post",
            # Category permissions
            "view_category",
            "add_category",
            "change_category",
            "delete_category",
            # Tag permissions
            "view_tag",
            "add_tag",
            "change_tag",
            "delete_tag",
            # Media permissions
            "view_media",
            "add_media",
            "change_media",
            "delete_media",
            "change_other_media",
        ]
        editor_group, created = Group.objects.get_or_create(name="djpress_editor")
        if created:
            logger.info("Created 'djpress_editor' group")
        editor_group.permissions.set([perm_map[code] for code in editor_codenames if code in perm_map])

        # 3. Author Group
        author_codenames = [
            # Post permissions
            "view_post",
            "add_post",
            "change_post",
            "can_publish_post",
            "can_soft_delete_post",
            "can_restore_post",
            # Tag permissions
            "view_tag",
            "add_tag",
            # Media permissions
            "view_media",
            "add_media",
            "change_media",
        ]
        author_group, created = Group.objects.get_or_create(name="djpress_author")
        if created:
            logger.info("Created 'djpress_author' group")
        author_group.permissions.set([perm_map[code] for code in author_codenames if code in perm_map])

        # 4. Contributor Group
        contributor_codenames = [
            # Post permissions
            "view_post",
            "add_post",
            "change_post",
            # Category permissions
            "view_category",
            # Tag permissions
            "view_tag",
            "add_tag",
            # Media permissions
            "view_media",
            "add_media",
        ]
        contributor_group, created = Group.objects.get_or_create(name="djpress_contributor")
        if created:
            logger.info("Created 'djpress_contributor' group")
        contributor_group.permissions.set([perm_map[code] for code in contributor_codenames if code in perm_map])

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
