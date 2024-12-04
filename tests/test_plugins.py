import pytest
from djpress.plugins import PluginRegistry, DJPressPlugin, Hooks
from djpress.plugins import registry
from djpress.exceptions import PluginLoadError

from djpress.conf import settings as djpress_settings


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


def test_hook_enum_values():
    """Test that Hook enum has the expected values."""
    assert Hooks.PRE_RENDER_CONTENT.value == "pre_render_content"
    assert Hooks.POST_RENDER_CONTENT.value == "post_render_content"


# Tests for plugin registration (flexible)
def test_register_hook_with_enum(clean_registry):
    """Test registering hook using Enum."""

    def test_callback(content: str) -> str:
        return content

    registry.register_hook(Hooks.PRE_RENDER_CONTENT, test_callback)
    assert Hooks.PRE_RENDER_CONTENT in registry.hooks
    assert test_callback in registry.hooks[Hooks.PRE_RENDER_CONTENT]


def test_register_hook_with_valid_string(clean_registry):
    """Test registering hook using valid string name."""

    def test_callback(content: str) -> str:
        return content

    registry.register_hook("pre_render_content", test_callback)
    assert Hooks.PRE_RENDER_CONTENT in registry.hooks
    assert test_callback in registry.hooks[Hooks.PRE_RENDER_CONTENT]


def test_register_unknown_hook_name(clean_registry):
    """Test registering unknown hook name - should accept but trigger warning."""

    def test_callback(content: str) -> str:
        return content

    registry.register_hook("unknown_hook", test_callback)
    assert "unknown_hook" in registry.hooks
    assert test_callback in registry.hooks["unknown_hook"]


# Tests for hook execution (strict)
def test_run_hook_with_enum(clean_registry):
    """Test running hook with Enum succeeds."""

    def test_callback(content: str) -> str:
        return content + " modified"

    registry.register_hook(Hooks.PRE_RENDER_CONTENT, test_callback)
    result = registry.run_hook(Hooks.PRE_RENDER_CONTENT, "test value")
    assert result == "test value modified"


# Tests for hook execution (strict)
def test_run_hook_with_multiple_hooks(clean_registry):
    """Test running hook with multiple hooks."""

    def test_callback(content: str) -> str:
        return content + " modified by test_callback"

    def second_test_callback(content: str) -> str:
        return content + " modified by second test_callback"

    registry.register_hook(Hooks.PRE_RENDER_CONTENT, test_callback)
    registry.register_hook(Hooks.PRE_RENDER_CONTENT, second_test_callback)
    result = registry.run_hook(Hooks.PRE_RENDER_CONTENT, "test value")
    assert result == "test value modified by test_callback modified by second test_callback"


def test_run_hook_with_exception(clean_registry):
    """Test running hook with an exception doesn't modify the value."""

    def test_callback(content: str) -> str:
        raise ValueError("Test error")

    registry.register_hook(Hooks.PRE_RENDER_CONTENT, test_callback)
    result = registry.run_hook(Hooks.PRE_RENDER_CONTENT, "test value")
    assert result == "test value"


def test_run_hook_with_string_fails(clean_registry):
    """Test running hook with string fails."""
    with pytest.raises(TypeError, match="hook_name must be a Hooks enum member"):
        registry.run_hook("pre_render_content", "test")


def test_run_hook_type_error_message(clean_registry):
    """Test specific error message when running hook with wrong type."""
    with pytest.raises(TypeError) as exc_info:
        registry.run_hook("pre_render_content", "test")
    assert "hook_name must be a Hooks enum member" in str(exc_info.value)
    assert "got <class 'str'>" in str(exc_info.value)


# For lines 48-50 (contextlib.suppress for ValueError)
def test_register_hook_with_invalid_string(clean_registry):
    """Test registering hook with invalid string - should store as string."""

    def test_callback(content: str) -> str:
        return content

    registry.register_hook("not_a_real_hook", test_callback)
    # Should store with string key since conversion to Enum failed
    assert "not_a_real_hook" in registry.hooks
    assert test_callback in registry.hooks["not_a_real_hook"]


# For line 90 (value is None in hooks dict)
def test_run_hook_nonexistent_hook(clean_registry):
    """Test running hook that hasn't been registered."""
    result = registry.run_hook(Hooks.PRE_RENDER_CONTENT, "test")
    assert result == "test"  # Should return original value unchanged


# For lines 96-98 (plugin loading already done)
def test_load_plugins_already_loaded(clean_registry):
    """Test that load_plugins doesn't reload if already loaded."""
    registry._loaded = True
    registry.load_plugins()
    assert len(registry.plugins) == 0  # Should not have loaded any plugins


# For lines 115-131 (_import_plugin_class)
def test_import_plugin_standard_location(clean_registry, tmp_path):
    """Test importing plugin from standard location."""
    # Create a temporary plugin package
    plugin_dir = tmp_path / "test_plugin"
    plugin_dir.mkdir()
    (plugin_dir / "__init__.py").write_text("")
    (plugin_dir / "plugin.py").write_text("""
from djpress.plugins import DJPressPlugin
class Plugin(DJPressPlugin):
    name = "test_plugin"
    """)

    # Add to Python path and try to import
    import sys

    sys.path.insert(0, str(tmp_path))

    try:
        plugin_class = registry._import_plugin_class("test_plugin")
        assert plugin_class.__name__ == "Plugin"
    finally:
        sys.path.pop(0)


def test_import_plugin_custom_location(clean_registry, tmp_path):
    """Test importing plugin from custom location."""
    # Similar setup but with custom path
    # Test both successful and failing imports


# For lines 147-165 and 175-178 (_instantiate_plugin)
def test_instantiate_plugin_with_config(clean_registry):
    """Test instantiating plugin with configuration."""

    class TestPlugin(DJPressPlugin):
        name = "test_plugin"

    plugin_settings = {"test_plugin": {"setting": "value"}}
    plugin = registry._instantiate_plugin(TestPlugin, "test_plugin", plugin_settings)
    assert isinstance(plugin, DJPressPlugin)
    assert plugin.config == {"setting": "value"}


def test_instantiate_plugin_fails(clean_registry):
    """Test handling of plugin instantiation failure."""

    class BrokenPlugin(DJPressPlugin):
        name = "broken_plugin"

        def __init__(self, config=None):
            raise RuntimeError("Plugin broken")

    from django.core.exceptions import ImproperlyConfigured

    with pytest.raises(ImproperlyConfigured) as exc_info:
        registry._instantiate_plugin(BrokenPlugin, "broken_plugin", {})
    assert "Error initializing plugin" in str(exc_info.value)


# For lines 48-50 (contextlib.suppress and string conversion)
def test_register_hook_conversion_from_string(clean_registry):
    """Test string to enum conversion in register_hook."""

    def callback(content: str) -> str:
        return content

    # This should try to convert the string to enum and succeed
    registry.register_hook("pre_render_content", callback)
    assert Hooks.PRE_RENDER_CONTENT in registry.hooks

    # This should try to convert and silently fail
    registry.register_hook("not_a_hook", callback)
    assert "not_a_hook" in registry.hooks


# For lines 96-98 (early return if already loaded)
def test_load_plugins_early_return(clean_registry):
    """Test that load_plugins returns early if already loaded."""
    registry._loaded = True
    original_plugins = registry.plugins.copy()
    registry.load_plugins()
    assert registry.plugins == original_plugins


# For lines 123-131 (import error handling)
def test_import_plugin_both_paths_fail(clean_registry):
    """Test when both import attempts fail."""
    from django.core.exceptions import ImproperlyConfigured

    with pytest.raises(ImproperlyConfigured) as exc_info:
        registry._import_plugin_class("nonexistent_plugin")

    assert "Could not load plugin 'nonexistent_plugin'" in str(exc_info.value)
    assert "Tried both custom path and standard plugin.py location" in str(exc_info.value)


# For lines 176-177 (plugin instantiation error)
def test_instantiate_plugin_setup_fails(clean_registry):
    """Test handling of plugin setup failure."""

    class PluginWithBadSetup(DJPressPlugin):
        name = "bad_setup"

        def setup(self, registry):
            raise RuntimeError("Setup failed")

    from django.core.exceptions import ImproperlyConfigured

    with pytest.raises(ImproperlyConfigured) as exc_info:
        registry._instantiate_plugin(PluginWithBadSetup, "bad_setup", {})

    assert "Error initializing plugin 'bad_setup'" in str(exc_info.value)


def test_register_hook_first_callback(clean_registry):
    """Test registering first callback for a hook."""

    def callback(content: str) -> str:
        return content

    # This should create new list and add callback
    registry.register_hook(Hooks.PRE_RENDER_CONTENT, callback)
    assert len(registry.hooks[Hooks.PRE_RENDER_CONTENT]) == 1
    assert registry.hooks[Hooks.PRE_RENDER_CONTENT][0] == callback


def test_load_plugins_successful(clean_registry, monkeypatch):
    """Test successful plugin loading process."""

    class TestPlugin(DJPressPlugin):
        name = "test"

        def setup(self, registry):
            pass

    # Mock the import and instantiate methods to return known values
    def mock_import(self, path):
        return TestPlugin

    def mock_instantiate(self, plugin_class, path, settings):
        return TestPlugin()

    monkeypatch.setattr(PluginRegistry, "_import_plugin_class", mock_import)
    monkeypatch.setattr(PluginRegistry, "_instantiate_plugin", mock_instantiate)

    # Set up test settings
    monkeypatch.setattr(djpress_settings, "PLUGINS", ["test_plugin"])
    monkeypatch.setattr(djpress_settings, "PLUGIN_SETTINGS", {})

    # Load plugins
    registry.load_plugins()

    # Verify plugin was added
    assert len(registry.plugins) == 1
    assert isinstance(registry.plugins[0], TestPlugin)


def test_load_plugins_exception(clean_registry, monkeypatch):
    """Test plugin loading with exception."""

    class TestPlugin(DJPressPlugin):
        name = "test"

        def setup(self, registry):
            pass

    # Mock the import and instantiate methods to return known values
    def mock_import(self, path):
        return TestPlugin

    def mock_instantiate(self, plugin_class, path, settings):
        raise RuntimeError("Plugin setup failed")

    monkeypatch.setattr(PluginRegistry, "_import_plugin_class", mock_import)
    monkeypatch.setattr(PluginRegistry, "_instantiate_plugin", mock_instantiate)

    # Set up test settings
    monkeypatch.setattr(djpress_settings, "PLUGINS", ["test_plugin"])
    monkeypatch.setattr(djpress_settings, "PLUGIN_SETTINGS", {})

    # Load plugins - will raise exception
    with pytest.raises(PluginLoadError):
        registry.load_plugins()


def test_plugin_missing_name():
    """Test plugin initialization with missing name."""

    class NoNamePlugin(DJPressPlugin):
        pass  # No name defined

    with pytest.raises(ValueError) as exc_info:
        NoNamePlugin()
    assert str(exc_info.value) == "Plugin must define a name"


def test_register_multiple_callbacks(clean_registry):
    """Test registering multiple callbacks for the same hook."""

    def callback1(content: str) -> str:
        return content + "1"

    def callback2(content: str) -> str:
        return content + "2"

    # Register first callback - should create new list
    registry.register_hook(Hooks.PRE_RENDER_CONTENT, callback1)
    assert len(registry.hooks[Hooks.PRE_RENDER_CONTENT]) == 1
    assert registry.hooks[Hooks.PRE_RENDER_CONTENT][0] == callback1

    # Register second callback - should append to existing list
    registry.register_hook(Hooks.PRE_RENDER_CONTENT, callback2)
    assert len(registry.hooks[Hooks.PRE_RENDER_CONTENT]) == 2
    assert registry.hooks[Hooks.PRE_RENDER_CONTENT][0] == callback1
    assert registry.hooks[Hooks.PRE_RENDER_CONTENT][1] == callback2

    # Verify both callbacks are executed in order
    result = registry.run_hook(Hooks.PRE_RENDER_CONTENT, "test")
    assert result == "test12"


def test_content_modification_hook(clean_registry):
    """Test hooks that modify and return content."""

    def test_callback(content: str) -> str:
        return content + " modified"

    registry.register_hook(Hooks.PRE_RENDER_CONTENT, test_callback)
    result = registry.run_hook(Hooks.PRE_RENDER_CONTENT, "test")
    assert result == "test modified"


@pytest.mark.django_db
def test_plugin_storage_interface():
    """Test plugin storage interface methods."""

    class TestPlugin(DJPressPlugin):
        name = "test_plugin"

    plugin = TestPlugin()

    # Test get_data with no storage
    assert plugin.get_data() == {}

    # Test save_data and get_data
    plugin.save_data({"key": "value"})
    assert plugin.get_data() == {"key": "value"}

    # Test save_data with update
    plugin.save_data({"new_key": "new_value"})
    assert plugin.get_data() == {"new_key": "new_value"}

    # Test save additional data
    data = plugin.get_data()
    data["extra"] = "data"
    plugin.save_data(data)
    assert plugin.get_data() == {"new_key": "new_value", "extra": "data"}
