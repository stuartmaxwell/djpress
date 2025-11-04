import pytest
from unittest.mock import patch

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.core.exceptions import ObjectDoesNotExist
from django.db import OperationalError, ProgrammingError

from djpress.models import Post
from djpress.permissions import create_groups


@pytest.fixture
def post_content_type() -> ContentType:
    return ContentType.objects.get_for_model(Post)


@pytest.mark.django_db
def test_group_permissions(post_content_type: ContentType) -> None:
    admin = Group.objects.get(name="djpress_admin")
    editor = Group.objects.get(name="djpress_editor")
    author = Group.objects.get(name="djpress_author")
    contributor = Group.objects.get(name="djpress_contributor")

    # Check publish permission
    publish_perm = Permission.objects.get(content_type=post_content_type, codename="can_publish_post")
    assert publish_perm in admin.permissions.all()
    assert publish_perm in editor.permissions.all()
    assert publish_perm in author.permissions.all()
    assert publish_perm not in contributor.permissions.all()


@pytest.mark.django_db
def test_group_category_permissions(post_content_type: ContentType) -> None:
    admin = Group.objects.get(name="djpress_admin")
    editor = Group.objects.get(name="djpress_editor")
    author = Group.objects.get(name="djpress_author")
    contributor = Group.objects.get(name="djpress_contributor")

    # Check category permissions
    category_perms = Permission.objects.filter(
        content_type=post_content_type, codename__in=["add_category", "change_category", "delete_category"]
    )
    for perm in category_perms:
        assert perm in admin.permissions.all()
        assert perm in editor.permissions.all()
        assert perm not in author.permissions.all()
        assert perm not in contributor.permissions.all()


@pytest.mark.django_db
def test_create_groups_handles_operational_error(caplog):
    """Test that create_groups handles OperationalError gracefully."""
    with caplog.at_level("DEBUG"):
        with patch("djpress.permissions.ContentType.objects.get_for_model") as mock_get_for_model:
            mock_get_for_model.side_effect = OperationalError("Database connection error")

            # Should not raise an exception
            create_groups()

            # Check that error was logged
            assert "Cannot create groups yet - database not ready" in caplog.text


@pytest.mark.django_db
def test_create_groups_handles_programming_error(caplog):
    """Test that create_groups handles ProgrammingError gracefully."""
    with caplog.at_level("DEBUG"):
        with patch("djpress.permissions.ContentType.objects.get_for_model") as mock_get_for_model:
            mock_get_for_model.side_effect = ProgrammingError("Table does not exist")

            # Should not raise an exception
            create_groups()

            # Check that error was logged
            assert "Cannot create groups yet - database not ready" in caplog.text


@pytest.mark.django_db
def test_create_groups_handles_object_does_not_exist(caplog):
    """Test that create_groups handles ObjectDoesNotExist gracefully."""
    with caplog.at_level("DEBUG"):
        with patch("djpress.permissions.Permission.objects.get") as mock_get:
            mock_get.side_effect = ObjectDoesNotExist("Permission does not exist")

            # Should not raise an exception
            create_groups()

            # Check that error was logged
            assert "Cannot create groups yet - models not ready" in caplog.text


@pytest.mark.django_db
def test_create_groups_handles_unexpected_error(caplog):
    """Test that create_groups handles unexpected exceptions gracefully."""
    with caplog.at_level("ERROR"):
        with patch("djpress.permissions.ContentType.objects.get_for_model") as mock_get_for_model:
            mock_get_for_model.side_effect = ValueError("Unexpected error")

            # Should not raise an exception
            create_groups()

            # Check that error was logged
            assert "Unexpected error creating groups" in caplog.text


@pytest.mark.django_db
def test_create_groups_logs_on_new_group_creation(caplog):
    """Test that create_groups logs when creating new groups."""
    # Delete all groups first
    Group.objects.filter(name__in=["djpress_admin", "djpress_editor", "djpress_author", "djpress_contributor"]).delete()

    with caplog.at_level("INFO"):
        create_groups()

    # Check that creation was logged for all groups
    assert "Created 'djpress_admin' group" in caplog.text
    assert "Created 'djpress_editor' group" in caplog.text
    assert "Created 'djpress_author' group" in caplog.text
    assert "Created 'djpress_contributor' group" in caplog.text
    assert "Successfully configured DJ Press groups and permissions" in caplog.text
