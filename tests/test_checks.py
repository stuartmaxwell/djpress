import pytest
from django.core.checks import Warning, run_checks
from djpress.checks import check_deprecated_settings, check_plugin_loading
from djpress.plugins import DJPressPlugin, registry


def test_plugin_error_creates_django_warning():
    # Simulate a plugin load error
    registry.plugin_errors.clear()
    registry.plugin_errors.append("Plugin error message")

    # Now call the system check function directly
    result = check_plugin_loading(None)

    # One warning should be returned
    assert len(result) == 1

    # It should be a Django Warning
    warning = result[0]
    from django.core.checks import Warning as DjangoWarning

    assert isinstance(warning, DjangoWarning)

    # Check the messge
    assert "Plugin error message" in warning.msg

    # check the warning id
    assert warning.id == "djpress.W001"


def test_plugin_check_clean_when_no_errors():
    registry.plugin_errors.clear()
    result = check_plugin_loading(None)
    assert result == []


@pytest.mark.django_db
def test_check_plugin_loading_with_django_checks(registry):
    """Test that the check_plugin_loading function works with Django's checks framework."""
    # Clear any existing plugin errors
    registry.plugin_errors.clear()

    # Run the checks
    warnings = run_checks()

    # Check that no warnings are returned when there are no plugin errors
    assert len(warnings) == 0


def test_deprecated_setting_creates_django_warning(settings):
    """A deprecated setting name in DJPRESS_SETTINGS should produce a djpress.W002 warning."""
    settings.DJPRESS_SETTINGS = {
        "MARKDOWN_RENDERER": "djpress.markdown_renderer.default_renderer",
    }

    result = check_deprecated_settings()

    assert len(result) == 1
    warning = result[0]
    assert isinstance(warning, Warning)
    assert "MARKDOWN_RENDERER is deprecated" in warning.msg
    assert warning.hint == "Rename MARKDOWN_RENDERER to CONTENT_RENDERER in DJPRESS_SETTINGS."
    assert warning.id == "djpress.W002"


def test_deprecated_settings_check_clean_when_not_configured(settings):
    """No warnings should be returned when only current setting names are configured."""
    settings.DJPRESS_SETTINGS = {
        "CONTENT_RENDERER": "djpress.markdown_renderer.default_renderer",
    }

    assert check_deprecated_settings() == []


@pytest.mark.django_db
def test_check_deprecated_settings_with_django_checks(settings, registry):
    """Test that the check_deprecated_settings function works with Django's checks framework."""
    registry.plugin_errors.clear()
    settings.DJPRESS_SETTINGS = {
        "MARKDOWN_RENDERER": "djpress.markdown_renderer.default_renderer",
    }

    warnings = run_checks()

    assert len(warnings) == 1
    assert warnings[0].id == "djpress.W002"
