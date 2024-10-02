import pytest
import importlib

from django.test import override_settings
from django.urls import reverse, resolve, NoReverseMatch, clear_url_caches

from djpress import urls as djpress_urls
from djpress.conf import settings

from example.config import urls as example_urls


def test_category_posts_url():
    """Test that the URL is correctly set when CATEGORY_ENABLED is True."""
    # Check default settings
    assert settings.CATEGORY_ENABLED is True
    assert settings.CATEGORY_PREFIX == "test-url-category"

    url = reverse("djpress:category_posts", kwargs={"slug": "test-slug"})
    assert url == "/test-url-category/test-slug/"


@pytest.mark.urls("djpress.urls")
def test_category_posts_url_no_CATEGORY_ENABLED():
    """Test that the URL is correctly set when CATEGORY_ENABLED is True."""
    # Check default settings
    assert settings.CATEGORY_ENABLED is True
    assert settings.CATEGORY_PREFIX == "test-url-category"

    settings.set("CATEGORY_ENABLED", False)
    assert settings.CATEGORY_ENABLED is False

    # Clear the URL caches
    clear_url_caches()

    # Reload the URL module to reflect the changed settings
    importlib.reload(djpress_urls)

    # Try to reverse the URL and check if it's not registered
    with pytest.raises(NoReverseMatch):
        reverse("djpress:category_posts", kwargs={"slug": "test-slug"})

    # Set back to default value
    settings.set("CATEGORY_ENABLED", True)
    assert settings.CATEGORY_ENABLED is True


def test_author_posts_url():
    """Test that the URL is correctly set when AUTHOR_ENABLED is True."""
    # Check default settings
    assert settings.AUTHOR_ENABLED is True
    assert settings.AUTHOR_PREFIX == "test-url-author"

    url = reverse("djpress:author_posts", kwargs={"author": "test-author"})
    assert url == "/test-url-author/test-author/"


@pytest.mark.urls("djpress.urls")
def test_author_posts_url_no_AUTHOR_ENABLED():
    """Test that the URL is correctly set when AUTHOR_ENABLED is True."""
    # Check default settings
    assert settings.AUTHOR_ENABLED is True
    assert settings.AUTHOR_PREFIX == "test-url-author"

    settings.set("AUTHOR_ENABLED", False)
    assert settings.AUTHOR_ENABLED is False

    # Clear the URL caches
    clear_url_caches()

    # Reload the URL module to reflect the changed settings
    importlib.reload(djpress_urls)

    # Try to reverse the URL and check if it's not registered
    with pytest.raises(NoReverseMatch):
        reverse("djpress:author_posts", kwargs={"author": "test-author"})

    # Set back to default value
    settings.set("AUTHOR_ENABLED", True)
    assert settings.AUTHOR_ENABLED is True


def test_archive_posts_url():
    """Test that the URL is correctly set when ARCHIVES_ENABLED is True."""
    # Check default settings
    assert settings.ARCHIVE_ENABLED is True
    assert settings.ARCHIVE_PREFIX == "test-url-archives"

    url = reverse("djpress:archive_posts", kwargs={"year": "2024"})
    assert url == "/test-url-archives/2024/"


@pytest.mark.urls("djpress.urls")
def test_archive_posts_url_no_ARCHIVES_ENABLED():
    """Test that the URL is correctly set when ARCHIVES_ENABLED is True."""
    # Check default settings
    assert settings.ARCHIVE_ENABLED is True
    assert settings.ARCHIVE_PREFIX == "test-url-archives"

    settings.set("ARCHIVE_ENABLED", False)
    assert settings.ARCHIVE_ENABLED is False

    # Clear the URL caches
    clear_url_caches()

    # Reload the URL module to reflect the changed settings
    importlib.reload(djpress_urls)

    # Try to reverse the URL and check if it's not registered
    with pytest.raises(NoReverseMatch):
        reverse("djpress:archive_posts", kwargs={"year": "2024"})

    # Set back to default value
    settings.set("ARCHIVE_ENABLED", True)
    assert settings.ARCHIVE_ENABLED is True


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


@override_settings(POST_PREFIX="post/{{ year }}/{{ month }}/{{ day }}")
@pytest.mark.urls("example.config.urls")
def test_single_post_text_year_month_day():
    """Test the single_post URL."""
    assert settings.POST_PREFIX == "post/{{ year }}/{{ month }}/{{ day }}"
    clear_url_caches()
    importlib.reload(djpress_urls)
    importlib.reload(example_urls)
    url = reverse("djpress:single_post", kwargs={"slug": "test-slug", "year": "2024", "month": "01", "day": "31"})
    assert url == "/post/2024/01/31/test-slug"


@override_settings(POST_PREFIX="post/{{ year }}/{{ month }}")
@pytest.mark.urls("example.config.urls")
def test_single_post_text_year_month():
    """Test the single_post URL."""
    assert settings.POST_PREFIX == "post/{{ year }}/{{ month }}"
    clear_url_caches()
    importlib.reload(djpress_urls)
    importlib.reload(example_urls)
    url = reverse("djpress:single_post", kwargs={"slug": "test-slug", "year": "2024", "month": "01"})
    assert url == "/post/2024/01/test-slug"


@override_settings(POST_PREFIX="post/{{ year }}")
@pytest.mark.urls("example.config.urls")
def test_single_post_text_year():
    """Test the single_post URL."""
    clear_url_caches()
    importlib.reload(djpress_urls)
    importlib.reload(example_urls)
    url = reverse("djpress:single_post", kwargs={"slug": "test-slug", "year": "2024"})
    assert url == "/post/2024/test-slug"


@override_settings(POST_PREFIX="post")
@pytest.mark.urls("example.config.urls")
def test_single_post_text():
    """Test the single_post URL."""
    clear_url_caches()
    importlib.reload(djpress_urls)
    importlib.reload(example_urls)
    url = reverse("djpress:single_post", kwargs={"slug": "test-slug"})
    assert url == "/post/test-slug"


@override_settings(POST_PREFIX="")
@pytest.mark.urls("example.config.urls")
def test_single_post_no_prefix():
    """Test the single_post URL."""
    clear_url_caches()
    importlib.reload(djpress_urls)
    importlib.reload(example_urls)
    url = reverse("djpress:single_post", kwargs={"slug": "test-slug"})
    assert url == "/test-slug"
