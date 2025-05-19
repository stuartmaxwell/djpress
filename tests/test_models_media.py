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
