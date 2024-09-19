import pytest
import importlib

from django.urls import reverse, resolve, NoReverseMatch, clear_url_caches

from djpress import urls as djpress_urls
from djpress.conf import settings
from djpress.urls import regex_path, regex_archives


def test_regex_path():
    """Test that the URL is correctly set when APPEND_SLASH is True."""
    # Default value is True
    assert settings.APPEND_SLASH is True

    # Test that the URL is correctly set
    assert regex_path() == r"^(?P<path>[0-9A-Za-z/_-]*)/$"

    settings.set("APPEND_SLASH", False)
    assert settings.APPEND_SLASH is False

    # Test that the URL is correctly set
    assert regex_path() == r"^(?P<path>[0-9A-Za-z/_-]*)$"

    # Set back to default value
    settings.set("APPEND_SLASH", True)
    assert settings.APPEND_SLASH is True


def test_regex_archives():
    """Test that the URL is correctly set when APPEND_SLASH is True."""
    # Default value is True
    assert settings.APPEND_SLASH is True

    # Test that the URL is correctly set
    assert (
        regex_archives()
        == r"(?P<year>\d{4})(?:/(?P<month>\d{2})(?:/(?P<day>\d{2}))?)?/$"
    )

    settings.set("APPEND_SLASH", False)
    assert settings.APPEND_SLASH is False

    # Test that the URL is correctly set
    assert (
        regex_archives()
        == r"(?P<year>\d{4})(?:/(?P<month>\d{2})(?:/(?P<day>\d{2}))?)?$"
    )

    # Set back to default value
    settings.set("APPEND_SLASH", True)
    assert settings.APPEND_SLASH is True


def test_category_posts_url():
    """Test that the URL is correctly set when CATEGORY_PATH_ENABLED is True."""
    # Check default settings
    assert settings.CATEGORY_PATH_ENABLED is True
    assert settings.CATEGORY_PATH == "test-url-category"

    url = reverse("djpress:category_posts", kwargs={"slug": "test-slug"})
    assert url == "/test-url-category/test-slug/"


@pytest.mark.urls("djpress.urls")
def test_category_posts_url_no_CATEGORY_PATH_ENABLED():
    """Test that the URL is correctly set when CATEGORY_PATH_ENABLED is True."""
    # Check default settings
    assert settings.CATEGORY_PATH_ENABLED is True
    assert settings.CATEGORY_PATH == "test-url-category"

    settings.set("CATEGORY_PATH_ENABLED", False)
    assert settings.CATEGORY_PATH_ENABLED is False

    # Clear the URL caches
    clear_url_caches()

    # Reload the URL module to reflect the changed settings
    importlib.reload(djpress_urls)

    # Try to reverse the URL and check if it's not registered
    with pytest.raises(NoReverseMatch):
        reverse("djpress:category_posts", kwargs={"slug": "test-slug"})

    # Set back to default value
    settings.set("CATEGORY_PATH_ENABLED", True)
    assert settings.CATEGORY_PATH_ENABLED is True


def test_author_posts_url():
    """Test that the URL is correctly set when AUTHOR_PATH_ENABLED is True."""
    # Check default settings
    assert settings.AUTHOR_PATH_ENABLED is True
    assert settings.AUTHOR_PATH == "test-url-author"

    url = reverse("djpress:author_posts", kwargs={"author": "test-author"})
    assert url == "/test-url-author/test-author/"


@pytest.mark.urls("djpress.urls")
def test_author_posts_url_no_AUTHOR_PATH_ENABLED():
    """Test that the URL is correctly set when AUTHOR_PATH_ENABLED is True."""
    # Check default settings
    assert settings.AUTHOR_PATH_ENABLED is True
    assert settings.AUTHOR_PATH == "test-url-author"

    settings.set("AUTHOR_PATH_ENABLED", False)
    assert settings.AUTHOR_PATH_ENABLED is False

    # Clear the URL caches
    clear_url_caches()

    # Reload the URL module to reflect the changed settings
    importlib.reload(djpress_urls)

    # Try to reverse the URL and check if it's not registered
    with pytest.raises(NoReverseMatch):
        reverse("djpress:author_posts", kwargs={"author": "test-author"})

    # Set back to default value
    settings.set("AUTHOR_PATH_ENABLED", True)
    assert settings.AUTHOR_PATH_ENABLED is True


def test_archives_posts_url():
    """Test that the URL is correctly set when ARCHIVES_PATH_ENABLED is True."""
    # Check default settings
    assert settings.ARCHIVES_PATH_ENABLED is True
    assert settings.ARCHIVES_PATH == "test-url-archives"

    url = reverse("djpress:archives_posts", kwargs={"year": "2024"})
    assert url == "/test-url-archives/2024/"


@pytest.mark.urls("djpress.urls")
def test_archives_posts_url_no_ARCHIVES_PATH_ENABLED():
    """Test that the URL is correctly set when ARCHIVES_PATH_ENABLED is True."""
    # Check default settings
    assert settings.ARCHIVES_PATH_ENABLED is True
    assert settings.ARCHIVES_PATH == "test-url-archives"

    settings.set("ARCHIVES_PATH_ENABLED", False)
    assert settings.ARCHIVES_PATH_ENABLED is False

    # Clear the URL caches
    clear_url_caches()

    # Reload the URL module to reflect the changed settings
    importlib.reload(djpress_urls)

    # Try to reverse the URL and check if it's not registered
    with pytest.raises(NoReverseMatch):
        reverse("djpress:archives_posts", kwargs={"year": "2024"})

    # Set back to default value
    settings.set("ARCHIVES_PATH_ENABLED", True)
    assert settings.ARCHIVES_PATH_ENABLED is True


def test_rss_feed_url():
    """Test that the URL is correctly set when RSS_ENABLED is True."""
    # Check default settings
    assert settings.RSS_ENABLED is True
    assert settings.RSS_PATH == "test-rss"

    url = reverse("djpress:rss_feed")
    assert url == "/test-rss/"


@pytest.mark.urls("djpress.urls")
def test_rss_feed_url_no_RSS_ENABLED():
    """Test that the URL is correctly set when RSS_ENABLED is True."""
    # Check default settings
    assert settings.RSS_ENABLED is True
    assert settings.RSS_PATH == "test-rss"

    settings.set("RSS_ENABLED", False)
    assert settings.RSS_ENABLED is False

    # Clear the URL caches
    clear_url_caches()

    # Reload the URL module to reflect the changed settings
    importlib.reload(djpress_urls)

    # Try to reverse the URL and check if it's not registered
    with pytest.raises(NoReverseMatch):
        reverse("djpress:rss_feed")

    # Set back to default value
    settings.set("RSS_ENABLED", True)
    assert settings.RSS_ENABLED is True
