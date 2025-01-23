import pytest

from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured
from django.core.checks import Error

from djpress.conf import settings as djpress_settings
from djpress.conf import check_djpress_settings


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
