import pytest

from django.conf import settings as django_settings
from django.core.cache import cache

from djpress.conf import Settings
from djpress import app_settings as default_settings


# A sample module for user settings
class CustomUserSettings:
    POST_PREFIX = "custom-prefix"
    POST_PERMALINK = "custom-permalink"
    CACHE_CATEGORIES = True
    CACHE_RECENT_PUBLISHED_POSTS = False


@pytest.fixture
def custom_settings():
    """Fixture to provide an instance of the Settings class with user and default settings."""
    return Settings(default_settings, CustomUserSettings)


def test_default_setting(custom_settings):
    """Test that default settings are returned correctly."""
    assert custom_settings.TRUNCATE_TAG == default_settings.TRUNCATE_TAG


def test_user_setting(custom_settings):
    """Test that user settings override default settings."""
    assert custom_settings.POST_PREFIX == "custom-prefix"
    assert not custom_settings.POST_PREFIX == default_settings.POST_PREFIX
    assert custom_settings.POST_PERMALINK == "custom-permalink"
    assert not custom_settings.POST_PERMALINK == default_settings.POST_PERMALINK


def test_missing_setting(custom_settings):
    """Test that accessing a non-existent setting raises an AttributeError."""
    with pytest.raises(AttributeError) as excinfo:
        _ = custom_settings.NON_EXISTENT_SETTING
    assert "Setting 'NON_EXISTENT_SETTING' not found" in str(excinfo.value)


@pytest.mark.django_db
def test_override_settings(custom_settings, settings):
    """Test overriding settings using the pytest-django settings fixture.

    This proves that the Django settings fixtures doesn't affect the custom settings."""
    assert custom_settings.POST_PREFIX == "custom-prefix"
    settings.POST_PREFIX = "overridden-prefix"
    assert django_settings.POST_PREFIX == "overridden-prefix"
    assert custom_settings.POST_PREFIX == "custom-prefix"

    assert custom_settings.POST_PERMALINK == "custom-permalink"
    settings.POST_PERMALINK = "overridden-permalink"
    assert django_settings.POST_PERMALINK == "overridden-permalink"
    assert custom_settings.POST_PERMALINK == "custom-permalink"


def test_cache_invalidation(custom_settings):
    """Test that changing a setting invalidates the cache if caching is enabled."""
    cache.set("test_key", "test_value")
    assert cache.get("test_key") == "test_value"

    custom_settings.set("NEW_SETTING", "new_value")
    assert cache.get("test_key") is None  # Cache should be invalidated

    # Temporarily override settings
    custom_settings.set("CACHE_CATEGORIES", False)
    custom_settings.set("CACHE_RECENT_PUBLISHED_POSTS", False)

    cache.set("test_key", "test_value")
    assert cache.get("test_key") == "test_value"

    custom_settings.set("ANOTHER_SETTING", "another_value")
    assert cache.get("test_key") == "test_value"  # Cache should not be invalidated


def test_change_settings_on_the_fly(custom_settings):
    """Test that changing a setting on the fly invalidates the cache if caching is enabled."""

    # First make sure the settings are configured in a way that the cache should be invalidated
    custom_settings.set("CACHE_CATEGORIES", True)
    custom_settings.set("CACHE_RECENT_PUBLISHED_POSTS", False)

    # Confirm that the settings are set correctly
    assert custom_settings.CACHE_CATEGORIES is True
    assert custom_settings.cache_categories is True
    assert custom_settings.CACHE_RECENT_PUBLISHED_POSTS is False
    assert custom_settings.cache_recent_published_posts is False
    assert custom_settings._should_invalidate_cache() is True

    cache.set("test_key", "test_value")
    assert cache.get("test_key") == "test_value"

    # Now we change a setting and this should invalidate the cache
    custom_settings.set("CACHE_CATEGORIES", False)

    assert custom_settings.CACHE_CATEGORIES is False
    assert custom_settings.cache_categories is False
    assert custom_settings._should_invalidate_cache() is False

    # The cache should be invalidated
    assert cache.get("test_key") is None

    # Set the cache again
    cache.set("test_key", "test_value")
    assert cache.get("test_key") == "test_value"

    # Now we change another setting and this should NOT invalidate the cache - this is
    # because there should be nothing in the cache to worry about. This is confirmed by
    # checking that _should_invalidate_cache is False
    assert custom_settings._should_invalidate_cache() is False
    custom_settings.set("CACHE_CATEGORIES", True)

    assert cache.get("test_key") == "test_value"

    # And now the cache should be invalidated because _should_invalidate_cache should be
    # True.
    assert custom_settings._should_invalidate_cache() is True
