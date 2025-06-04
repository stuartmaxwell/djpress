import pytest
from django.core.checks import Warning, run_checks
from djpress.checks import check_plugin_loading
from djpress.plugins import DJPressPlugin, registry, Hooks


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
def test_check_plugin_loading_with_django_checks(clean_registry):
    """Test that the check_plugin_loading function works with Django's checks framework."""
    # Clear any existing plugin errors
    registry.plugin_errors.clear()

    # Run the checks
    warnings = run_checks()

    # Check that no warnings are returned when there are no plugin errors
    assert len(warnings) == 0


@pytest.mark.django_db
def test_check_dirty_plugin_loading_with_django_checks(bad_plugin_registry):
    """Test that the check_plugin_loading function works with Django's checks framework."""
    # Clear any existing plugin errors
    # registry.plugin_errors.clear()

    # Run the checks
    result = run_checks()

    # One warning should be returned
    assert len(result) == 1

    # It should be a Django Warning
    warning = result[0]
    from django.core.checks import Warning as DjangoWarning

    assert isinstance(warning, DjangoWarning)

    # Check the message
    assert "Invalid hook str name: foobar. Hook not registered by callback" in warning.msg

    # check the warning id
    assert warning.id == "djpress.W001"
