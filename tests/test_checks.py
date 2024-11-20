import pytest
from django.core.checks import Warning
from djpress.checks import check_plugin_hooks
from djpress.plugins import DJPressPlugin, registry, Hooks


def test_check_valid_hooks(clean_registry):
    """Test that check passes with valid hooks."""

    def test_callback(content: str) -> str:
        return content

    registry.register_hook(Hooks.PRE_RENDER_CONTENT, test_callback)
    registry.register_hook(Hooks.POST_RENDER_CONTENT, test_callback)

    warnings = check_plugin_hooks(None)
    assert len(warnings) == 0


def test_check_unknown_hook(clean_registry):
    """Test that check warns about unknown hook that isn't a Hooks enum."""

    def test_callback(content: str) -> str:
        return content

    # Directly manipulate registry to bypass type checking
    registry.hooks["unknown_hook"] = [test_callback]

    warnings = check_plugin_hooks(None)
    assert len(warnings) == 1
    warning = warnings[0]
    assert isinstance(warning, Warning)
    assert warning.id == "djpress.W001"
    assert "unknown hook 'unknown_hook'" in str(warning)
    assert "deprecated hook or a hook from a newer version" in warning.hint


def test_check_multiple_hooks(clean_registry):
    """Test check with mix of valid and invalid hooks."""

    def test_callback(content: str) -> str:
        return content

    # Register valid hooks normally
    registry.register_hook(Hooks.PRE_RENDER_CONTENT, test_callback)
    registry.register_hook(Hooks.POST_RENDER_CONTENT, test_callback)

    # Directly add invalid hook to bypass type checking
    registry.hooks["unknown_hook"] = [test_callback]

    warnings = check_plugin_hooks(None)
    assert len(warnings) == 1  # Only one warning for the unknown hook
    assert "unknown hook 'unknown_hook'" in str(warnings[0])


def test_check_detects_plugin_with_unknown_hook(bad_plugin_registry):
    """Test that check system detects plugin using unknown hook."""
    warnings = check_plugin_hooks(None)
    print(warnings)
    assert len(warnings) == 1
    assert "unknown hook 'foobar'" in str(warnings[0])
