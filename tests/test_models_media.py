"""Test the Media model."""

from django.utils import timezone
import pytest

from datetime import datetime
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from djpress.conf import settings as djpress_settings
from djpress.models import Media


@pytest.mark.django_db
def test_media_file_creation(test_media_file_1, user):
    """Test creating a media object."""
    assert test_media_file_1.title == "Test Document"
    assert test_media_file_1.media_type == "document"
    assert test_media_file_1.description == "A test document"
    assert test_media_file_1.uploaded_by == user
    assert str(test_media_file_1), "Test Document"
    assert test_media_file_1.filename.endswith("test_file.txt")


@pytest.mark.django_db
def test_media_image_creation(test_media_image_1, user):
    """Test creating a media object."""
    assert test_media_image_1.title == "Test Image"
    assert test_media_image_1.media_type == "image"
    assert test_media_image_1.alt_text == "Test image alt text"
    assert test_media_image_1.description == "A test image"
    assert test_media_image_1.uploaded_by == user
    assert str(test_media_image_1), "Test Image"
    assert test_media_image_1.filename.endswith("test_image.jpg")


def test_upload_to_path():
    """Test the upload_to_path function."""

    # Create a test media instance
    test_media = Media(title="Test File")

    # Test with default path
    from djpress.models.media import upload_to_path

    path = upload_to_path(test_media, "test_file.txt")

    # The default path should be 'djpress/YYYY/MM/DD/filename'
    expected_path = f"djpress/{timezone.now().strftime('%Y')}/{timezone.now().strftime('%m')}/{timezone.now().strftime('%d')}/test_file.txt"
    assert path == expected_path


def test_custom_upload_path(settings):
    """Test custom upload path configuration."""

    settings.DJPRESS_SETTINGS["MEDIA_UPLOAD_PATH"] = "custom/{{ year }}-{{ month }}/"

    # Create a test media instance
    test_media = Media(title="Test File")

    # Test with custom path
    from djpress.models.media import upload_to_path

    path = upload_to_path(test_media, "test_file.txt")

    # The path should use our custom format
    expected_path = f"custom/{datetime.now().strftime('%Y')}-{datetime.now().strftime('%m')}/test_file.txt"
    assert path == expected_path


@pytest.mark.django_db
def test_manager_get_by_type(test_media_file_1, test_media_image_1):
    """Test the get_by_type manager method."""
    documents = Media.objects.get_by_type("document")
    images = Media.objects.get_by_type("image")

    assert documents.count() == 1
    assert images.count() == 1

    assert documents.first() == test_media_file_1
    assert images.first() == test_media_image_1


@pytest.mark.django_db
def test_file_size(test_media_file_1):
    """Test the file size property."""
    assert test_media_file_1.filesize == test_media_file_1.file.size
    assert test_media_file_1.filesize > 0


@pytest.mark.django_db
def test_file_url(test_media_file_1):
    """Test the file URL property."""
    assert test_media_file_1.file.url == test_media_file_1.url


@pytest.mark.django_db
def test_markdown_url(test_media_file_1, test_media_image_1):
    """Test the markdown URL property."""
    assert test_media_file_1.markdown_url == f"[{test_media_file_1.title}]({test_media_file_1.file.url})"
    assert (
        test_media_image_1.markdown_url
        == f'![{test_media_image_1.alt_text}]({test_media_image_1.file.url} "{test_media_image_1.title}")'
    )


@pytest.mark.django_db
def test_media_permission_helper_methods(test_media_file_1):
    """Test the permission helper methods for various user groups/roles on Media."""
    from django.contrib.auth import get_user_model
    from django.contrib.auth.models import Group
    from djpress.permissions import create_groups

    # Ensure groups are created
    create_groups()

    User = get_user_model()

    # Create users for each role
    admin_user = User.objects.create_user(username="admin_test_media", password="pass")
    admin_user.groups.add(Group.objects.get(name="djpress_admin"))

    editor_user = User.objects.create_user(username="editor_test_media", password="pass")
    editor_user.groups.add(Group.objects.get(name="djpress_editor"))

    author_user = User.objects.create_user(username="author_test_media", password="pass")
    author_user.groups.add(Group.objects.get(name="djpress_author"))

    other_author = User.objects.create_user(username="other_author_test_media", password="pass")
    other_author.groups.add(Group.objects.get(name="djpress_author"))

    contributor_user = User.objects.create_user(username="contrib_test_media", password="pass")
    contributor_user.groups.add(Group.objects.get(name="djpress_contributor"))

    other_contributor = User.objects.create_user(username="other_contrib_test_media", password="pass")
    other_contributor.groups.add(Group.objects.get(name="djpress_contributor"))

    superuser = User.objects.create_superuser(username="super_test_media", password="pass")

    # Set media uploaded_by to author_user
    test_media_file_1.uploaded_by = author_user
    test_media_file_1.save()

    # Test can_change
    assert test_media_file_1.can_change(superuser) is True
    assert test_media_file_1.can_change(admin_user) is True
    assert test_media_file_1.can_change(editor_user) is True
    assert test_media_file_1.can_change(author_user) is True
    assert test_media_file_1.can_change(other_author) is False
    assert test_media_file_1.can_change(contributor_user) is False

    # Set media uploaded_by to contributor_user
    test_media_file_1.uploaded_by = contributor_user
    test_media_file_1.save()

    assert test_media_file_1.can_change(superuser) is True
    assert test_media_file_1.can_change(admin_user) is True
    assert test_media_file_1.can_change(editor_user) is True
    assert test_media_file_1.can_change(contributor_user) is False
    assert test_media_file_1.can_change(other_contributor) is False
