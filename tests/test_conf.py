import pytest
from unittest.mock import patch

from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured
from django.core.checks import Error

from djpress.conf import settings as djpress_settings
from djpress.conf import check_djpress_settings
from django.core.exceptions import ValidationError
from djpress.models.setting import Setting
from django.core.cache import cache


def test_load_default_test_settings_example_project(settings):
    """Test that the default settings from the example project are loaded."""

    assert settings.DJPRESS_SETTINGS["SITE_TITLE"] == "My Test DJ Press Blog"
    assert settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] == 3
    assert settings.DJPRESS_SETTINGS["AUTHOR_PREFIX"] == "test-url-author"


def test_setting_not_overridden(settings):
    """Test that a setting not overridden in Django settings falls back to the default."""
    # We can query the setting from the DJ Press settings object - it will check the Django settings first and fall
    # back to the default value if not overridden
    assert djpress_settings.MARKDOWN_EXTENSIONS == []
    # The folllowing raises an error because the Django conf doesn't know about the setting
    with pytest.raises(KeyError):
        assert settings.DJPRESS_SETTINGS["MARKDOWN_EXTENSIONS"] == []

    # Now we can assign a value to the setting in the Django settings
    settings.DJPRESS_SETTINGS["MARKDOWN_EXTENSIONS"] = ["markdown.extensions.codehilite"]

    # The setting is now available in the DJ Press settings object
    assert djpress_settings.MARKDOWN_EXTENSIONS == ["markdown.extensions.codehilite"]

    # The setting is also available in the Django settings
    assert settings.DJPRESS_SETTINGS["MARKDOWN_EXTENSIONS"] == ["markdown.extensions.codehilite"]


def test_leaky_test(settings):
    with pytest.raises(KeyError):
        assert settings.DJPRESS_SETTINGS["MARKDOWN_EXTENSIONS"] == []


def test_override_settings_in_django_settings(settings):
    """Test that settings can be overridden in Django settings.py."""
    settings.DJPRESS_SETTINGS = {
        "SITE_TITLE": "Custom Blog Title",
        "RECENT_PUBLISHED_POSTS_COUNT": 10,
    }

    assert settings.DJPRESS_SETTINGS["SITE_TITLE"] == "Custom Blog Title"
    assert django_settings.DJPRESS_SETTINGS["SITE_TITLE"] == "Custom Blog Title"
    assert djpress_settings.SITE_TITLE == "Custom Blog Title"
    assert djpress_settings.RECENT_PUBLISHED_POSTS_COUNT == 10


def test_type_validation_for_overridden_settings(settings):
    """Test that settings enforce correct types."""
    # Valid setting with the correct type
    settings.DJPRESS_SETTINGS = {
        "ARCHIVE_ENABLED": False,
    }

    assert djpress_settings.ARCHIVE_ENABLED is False

    # Invalid setting type: should raise TypeError
    settings.DJPRESS_SETTINGS = {
        "ARCHIVE_ENABLED": "yes",  # Incorrect type
    }

    with pytest.raises(TypeError):
        _ = djpress_settings.ARCHIVE_ENABLED

    # Invalid setting type: should raise TypeError
    settings.DJPRESS_SETTINGS = {
        "ARCHIVE_ENABLED": 0,  # Incorrect type
    }

    with pytest.raises(TypeError):
        _ = djpress_settings.ARCHIVE_ENABLED


def test_int_validation_settings(settings):
    """Test that int settings are greater than or equal to 0."""
    # Valid setting with the correct value
    settings.DJPRESS_SETTINGS = {
        "MAX_TAGS_PER_QUERY": 5,
    }
    assert djpress_settings.MAX_TAGS_PER_QUERY == 5

    # Invalid setting with negative value: should raise ValueError
    settings.DJPRESS_SETTINGS = {
        "MAX_TAGS_PER_QUERY": -1,
    }
    with pytest.raises(ValueError):
        assert djpress_settings.MAX_TAGS_PER_QUERY == -1

    # Valid setting with zero value
    settings.DJPRESS_SETTINGS = {
        "MAX_TAGS_PER_QUERY": 0,
    }
    assert djpress_settings.MAX_TAGS_PER_QUERY == 0

    # Valid setting with the correct value
    settings.DJPRESS_SETTINGS = {
        "RECENT_PUBLISHED_POSTS_COUNT": 5,
    }
    assert djpress_settings.RECENT_PUBLISHED_POSTS_COUNT == 5

    # Invalid setting with negative value: should raise ValueError
    settings.DJPRESS_SETTINGS = {
        "RECENT_PUBLISHED_POSTS_COUNT": -1,
    }
    with pytest.raises(ValueError):
        assert djpress_settings.RECENT_PUBLISHED_POSTS_COUNT == -1

    # Valid setting with zero value
    settings.DJPRESS_SETTINGS = {
        "RECENT_PUBLISHED_POSTS_COUNT": 0,
    }
    assert djpress_settings.RECENT_PUBLISHED_POSTS_COUNT == 0


def test_invalid_setting_key():
    """Test that requesting an invalid setting raises an AttributeError."""
    with pytest.raises(AttributeError):
        _ = djpress_settings.INVALID_SETTING_KEY


def test_django_settings_not_defined_in_djpress(settings):
    """Test that Django settings not defined in DJPress are returned."""
    assert settings.APPEND_SLASH is True
    assert django_settings.APPEND_SLASH is True
    with pytest.raises(AttributeError):
        djpress_settings.APPEND_SLASH


def test_invalid_settings_rss(settings):
    """Test that invalid settings raise an ImproperlyConfigured error."""
    settings.DJPRESS_SETTINGS = {
        "RSS_ENABLED": True,
        "RSS_PATH": "",
    }
    errors = check_djpress_settings()
    assert len(errors) == 1
    assert errors[0] == Error(
        "RSS_PATH cannot be empty if RSS_ENABLED is True.",
        id="djpress.E001",
    )


def test_invalid_settings_category(settings):
    """Test that invalid settings raise an ImproperlyConfigured error."""
    settings.DJPRESS_SETTINGS = {
        "CATEGORY_ENABLED": True,
        "CATEGORY_PREFIX": "",
    }
    errors = check_djpress_settings()
    assert len(errors) == 1
    assert errors[0] == Error(
        "CATEGORY_PREFIX cannot be empty if CATEGORY_ENABLED is True.",
        id="djpress.E002",
    )


def test_invalid_settings_author(settings):
    """Test that invalid settings raise an ImproperlyConfigured error."""
    settings.DJPRESS_SETTINGS = {
        "AUTHOR_ENABLED": True,
        "AUTHOR_PREFIX": "",
    }
    errors = check_djpress_settings()
    assert len(errors) == 1
    assert errors[0] == Error(
        "AUTHOR_PREFIX cannot be empty if AUTHOR_ENABLED is True.",
        id="djpress.E003",
    )


def test_invalid_settings_tag(settings):
    """Test that invalid settings raise an ImproperlyConfigured error."""
    settings.DJPRESS_SETTINGS = {
        "TAG_ENABLED": True,
        "TAG_PREFIX": "",
    }
    errors = check_djpress_settings()
    assert len(errors) == 1
    assert errors[0] == Error(
        "TAG_PREFIX cannot be empty if TAG_ENABLED is True.",
        id="djpress.E004",
    )


def test_author_enabled_default_is_false(settings):
    """Test that AUTHOR_ENABLED defaults to False."""
    settings.DJPRESS_SETTINGS.clear()
    assert djpress_settings.AUTHOR_ENABLED is False


@pytest.mark.django_db
def test_dynamic_settings_disabled_by_default():
    """Test that database settings are disabled by default."""
    assert djpress_settings.DATABASE_SETTINGS_ENABLED is False

    # Create a setting in the database
    Setting.objects.create(key="SITE_TITLE", value="DB Site Title")

    # The lookup should NOT check the DB and should fall back to Django settings
    assert djpress_settings.SITE_TITLE == "My Test DJ Press Blog"


@pytest.mark.django_db
def test_dynamic_settings_precedence(settings):
    """Test that DB settings take precedence over Django settings when enabled."""
    # Enable database settings lookups
    settings.DJPRESS_SETTINGS = {
        "DATABASE_SETTINGS_ENABLED": True,
        "SITE_TITLE": "Django settings title",
    }

    assert djpress_settings.DATABASE_SETTINGS_ENABLED is True

    # Check initially it returns the Django settings value
    assert djpress_settings.SITE_TITLE == "Django settings title"

    # Create the setting in the database
    Setting.objects.create(key="SITE_TITLE", value="DB Site Title")

    # Database setting takes precedence!
    assert djpress_settings.SITE_TITLE == "DB Site Title"


@pytest.mark.django_db
def test_dynamic_settings_validation():
    """Test type validation for dynamic settings."""
    # Expected type for RSS_ENABLED is bool. Try setting to integer 123.
    setting = Setting(key="RSS_ENABLED", value=123)
    with pytest.raises(ValidationError) as exc_info:
        setting.full_clean()
    assert "Expected bool, got int" in str(exc_info.value)

    # Expected type for RECENT_PUBLISHED_POSTS_COUNT is int. Try setting to a negative number.
    setting = Setting(key="RECENT_PUBLISHED_POSTS_COUNT", value=-5)
    with pytest.raises(ValidationError) as exc_info:
        setting.full_clean()
    assert "must be greater than or equal to 0" in str(exc_info.value)

    # Valid values should clean successfully
    setting = Setting(key="RSS_ENABLED", value=False)
    setting.full_clean()  # should not raise


@pytest.mark.django_db
def test_dynamic_settings_lockout_prevention():
    """Test that DATABASE_SETTINGS_ENABLED is prevented from being saved in DB."""
    setting = Setting(key="DATABASE_SETTINGS_ENABLED", value=True)
    with pytest.raises(ValidationError) as exc_info:
        setting.full_clean()
    assert "DATABASE_SETTINGS_ENABLED is a system-level setting" in str(exc_info.value)


@pytest.mark.django_db
def test_dynamic_settings_unrecognized_keys(settings):
    """Test that unrecognized settings are saved without error but ignored."""
    settings.DJPRESS_SETTINGS = {
        "DATABASE_SETTINGS_ENABLED": True,
    }

    # Save an unrecognized key
    setting = Setting(key="SOME_CUSTOM_UNRECOGNIZED_KEY", value="custom_value")
    setting.full_clean()
    setting.save()

    # The settings object shouldn't resolve it (it raises AttributeError)
    with pytest.raises(AttributeError):
        _ = djpress_settings.SOME_CUSTOM_UNRECOGNIZED_KEY


@pytest.mark.django_db
def test_dynamic_settings_caching_and_invalidation(settings):
    """Test that dynamic settings cache is correctly invalidated on save/delete."""
    settings.DJPRESS_SETTINGS = {
        "DATABASE_SETTINGS_ENABLED": True,
        "SITE_TITLE": "Django Title",
    }

    # Clear cache first to ensure a clean state
    cache.delete("djpress:settings")

    # Initial query should set the cache (which will be empty since no DB settings exist yet)
    assert djpress_settings.SITE_TITLE == "Django Title"
    assert cache.get("djpress:settings") == {}

    # Creating a setting should invalidate the cache automatically via signals
    setting = Setting.objects.create(key="SITE_TITLE", value="DB Cached Title")
    assert cache.get("djpress:settings") is None  # Signal deleted it!

    # Querying again should hit the DB, refresh the cache, and return the new value
    assert djpress_settings.SITE_TITLE == "DB Cached Title"
    assert cache.get("djpress:settings") == {"SITE_TITLE": "DB Cached Title"}

    # Modifying the setting should invalidate the cache
    setting.value = "DB New Cached Title"
    setting.save()
    assert cache.get("djpress:settings") is None

    # Querying should refresh again
    assert djpress_settings.SITE_TITLE == "DB New Cached Title"
    assert cache.get("djpress:settings") == {"SITE_TITLE": "DB New Cached Title"}

    # Deleting the setting should invalidate the cache
    setting.delete()
    assert cache.get("djpress:settings") is None
    assert djpress_settings.SITE_TITLE == "Django Title"


def test_database_settings_enabled_invalid_type(settings):
    """Test that invalid type for DATABASE_SETTINGS_ENABLED in Django settings raises a TypeError."""
    settings.DJPRESS_SETTINGS = {
        "DATABASE_SETTINGS_ENABLED": "not-a-boolean",
    }
    with pytest.raises(TypeError) as exc_info:
        _ = djpress_settings.database_settings_enabled()
    assert "Expected bool for DATABASE_SETTINGS_ENABLED" in str(exc_info.value)


@pytest.mark.django_db
def test_dynamic_settings_runtime_type_error(settings):
    """Test that invalid DB value type raises TypeError at runtime."""
    settings.DJPRESS_SETTINGS = {
        "DATABASE_SETTINGS_ENABLED": True,
    }

    # Return invalid value for RSS_ENABLED (which expects bool) from DB
    with patch.object(djpress_settings, "_get_db_settings", return_value={"RSS_ENABLED": 123}):
        with pytest.raises(TypeError) as exc_info:
            _ = djpress_settings.RSS_ENABLED
        assert "Expected bool for RSS_ENABLED, got int" in str(exc_info.value)


@pytest.mark.django_db
def test_dynamic_settings_runtime_value_error(settings):
    """Test that negative int DB value raises ValueError at runtime."""
    settings.DJPRESS_SETTINGS = {
        "DATABASE_SETTINGS_ENABLED": True,
    }

    # Return invalid negative integer for RECENT_PUBLISHED_POSTS_COUNT from DB
    with patch.object(djpress_settings, "_get_db_settings", return_value={"RECENT_PUBLISHED_POSTS_COUNT": -5}):
        with pytest.raises(ValueError) as exc_info:
            _ = djpress_settings.RECENT_PUBLISHED_POSTS_COUNT
        assert "RECENT_PUBLISHED_POSTS_COUNT must be greater than or equal to 0" in str(exc_info.value)


@pytest.mark.django_db
def test_dynamic_settings_db_exception_graceful_fallback(settings):
    """Test that database exceptions during settings retrieval are caught and fall back gracefully."""
    settings.DJPRESS_SETTINGS = {
        "DATABASE_SETTINGS_ENABLED": True,
    }

    # Clear cache first to force a database query attempt
    cache.delete("djpress:settings")

    with patch.object(Setting.objects, "all", side_effect=Exception("DB Connection Error")):
        # Querying settings should not raise an exception, and should return the default value
        assert djpress_settings.SITE_TITLE == "My DJ Press Blog"


@pytest.mark.django_db
def test_setting_str_method():
    """Test the __str__ method of the Setting model."""
    setting = Setting(key="SITE_TITLE", value="My Test Title")
    assert str(setting) == "SITE_TITLE: My Test Title"
