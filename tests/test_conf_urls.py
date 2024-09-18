from django.urls import reverse

from djpress.conf import settings


def test_url_author_enabled():
    """Test the author URL."""

    # Confirm settings are set according to settings_testing.py
    assert settings.AUTHOR_PATH_ENABLED is True
    assert settings.AUTHOR_PATH == "test-url-author"

    author_url = reverse("djpress:author_posts", args=["test-author"])

    assert author_url == f"/{settings.AUTHOR_PATH}/test-author/"


def test_url_category_enabled():
    """Test the category URL."""

    # Confirm settings are set according to settings_testing.py
    assert settings.CATEGORY_PATH_ENABLED is True
    assert settings.CATEGORY_PATH == "test-url-category"

    category_url = reverse("djpress:category_posts", args=["test-category"])

    assert category_url == f"/{settings.CATEGORY_PATH}/test-category/"
