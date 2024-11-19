import pytest
from djpress.plugins import PluginRegistry, DJPressPlugin, Hooks
from djpress.plugins import registry


def test_registry_initialization():
    """Test that registry initializes with empty plugins and hooks."""
    registry = PluginRegistry()
    assert registry.plugins == []
    assert registry.hooks == {}
    assert registry._loaded is False


def test_register_hook():
    """Test registering a hook callback."""
    registry = PluginRegistry()

    def test_callback(content: str) -> str:
        return content

    registry.register_hook(Hooks.PRE_RENDER_CONTENT, test_callback)
    assert test_callback in registry.hooks[Hooks.PRE_RENDER_CONTENT]


def test_register_hook_with_enum(clean_registry):
    """Test that registering with a valid Hook enum works."""

    def test_callback(content: str) -> str:
        return content

    registry.register_hook(Hooks.PRE_RENDER_CONTENT, test_callback)
    assert Hooks.PRE_RENDER_CONTENT in registry.hooks
    assert test_callback in registry.hooks[Hooks.PRE_RENDER_CONTENT]


def test_register_hook_with_string_fails(clean_registry):
    """Test that registering with a string instead of Hook enum fails."""

    def test_callback(content: str) -> str:
        return content

    with pytest.raises(TypeError, match="hook_name must be a Hooks enum member"):
        registry.register_hook("pre_render_content", test_callback)


def test_run_hook_with_string_fails(clean_registry):
    """Test that running a hook with a string instead of Hook enum fails."""
    with pytest.raises(TypeError, match="hook_name must be a Hooks enum member"):
        registry.run_hook("pre_render_content", "some content")


def test_hook_enum_values():
    """Test that Hook enum has the expected values."""
    assert Hooks.PRE_RENDER_CONTENT.value == "pre_render_content"
    assert Hooks.POST_RENDER_CONTENT.value == "post_render_content"
