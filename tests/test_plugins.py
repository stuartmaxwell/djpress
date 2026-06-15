"""Tests for the DJ Press plugin system."""

import logging
from typing import Protocol
from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ImproperlyConfigured

# Import the components to be tested
from djpress.models import Post
from djpress.plugins import DJPressPlugin
from djpress.plugins.hook_registry import (
    DJPRESS_FOOTER,
    DJPRESS_HEADER,
    POST_RENDER_CONTENT,
    POST_SAVE_POST,
    PRE_RENDER_CONTENT,
    SEARCH_CONTENT,
    _Hook,
    _validate_hook_callback,
)
from djpress.plugins.plugin_registry import PluginRegistry
from djpress.plugins.protocols import ContentTransformer, SimpleContentProvider


class HeaderFooterPlugin(DJPressPlugin):
    """A plugin that adds content to the header and footer."""

    name = "Header/Footer Plugin"
    hooks = [
        (DJPRESS_HEADER, "render_header"),
        (DJPRESS_FOOTER, "render_footer"),
    ]

    def render_header(self) -> str:
        return "<!-- render_header HeaderFooterPlugin Plugin -->"

    def render_footer(self) -> str:
        return "<!-- render_footer HeaderFooterPlugin Plugin -->"


class PostSaveNotificationPlugin(DJPressPlugin):
    """A plugin that 'sends a notification' when a post is saved."""

    name = "Post-Save Notifier"
    hooks = [
        (POST_SAVE_POST, "send_notification"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.notification_sent = False
        self.saved_post_slug = ""

    def send_notification(self, post: object) -> None:
        """Simulates sending a notification."""
        self.notification_sent = True
        self.saved_post_slug = getattr(post, "slug", "unknown")


class PluginWithConfig(DJPressPlugin):
    """A plugin that uses configuration."""

    name = "Configurable Plugin"

    def get_greeting(self) -> str:
        return self.settings.get("greeting", "Hello")


class FaultyPlugin(DJPressPlugin):
    """A plugin designed to fail during initialization."""

    name = "Faulty Plugin"

    def __init__(self) -> None:
        # This will raise an exception
        super().__init__()
        raise RuntimeError("I am a faulty plugin!")


class PluginWithBadHooks(DJPressPlugin):
    """A plugin with a non-iterable hooks attribute."""

    name = "Bad Hooks Plugin"
    hooks = None  # type: ignore


def test_hook_equality_and_hash():
    """Test that Hooks with the same name are considered equal and have the same hash.

    Tests the `__eq__` method of the _Hook class.
    """
    hook1 = _Hook("my_hook", ContentTransformer)
    hook2 = _Hook("my_hook", SimpleContentProvider)
    hook3 = _Hook("another_hook", ContentTransformer)

    assert hook1 == hook2
    assert hook1 != hook3
    assert hook1 != "my_hook"
    assert hash(hook1) == hash(hook2)
    assert hash(hook1) != hash(hook3)


def test_validate_hook_callback():
    """Test the signature validation helper function."""

    def valid_content_transformer(content: str) -> str:
        return content

    def invalid_too_many_args(content: str, extra: int) -> str:
        return content

    def invalid_no_args() -> str:
        return ""

    def invalid_content_transformer(content: int) -> int:
        return content

    hook_no_protocol = _Hook("my_hook", None)  # type: ignore

    class BadProtocolWithNoCall:
        """A protocol whose __call__ method is not callable."""

        __call__ = 123

    BAD_HOOK = _Hook("static_empty_call_hook", BadProtocolWithNoCall)

    def callback_for_bad_protocol(content: str) -> str:
        """A standard callback, its signature won't be fully checked due to earlier error."""
        return content

    is_valid, msg = _validate_hook_callback(PRE_RENDER_CONTENT, valid_content_transformer)
    assert is_valid is True
    assert msg == ""

    is_valid, msg = _validate_hook_callback(PRE_RENDER_CONTENT, invalid_too_many_args)
    print(msg)
    assert is_valid is False
    assert "Callback requires 2 parameters, but hook only provides 1" in msg

    is_valid, msg = _validate_hook_callback(DJPRESS_HEADER, invalid_no_args)
    assert is_valid is True

    is_valid, msg = _validate_hook_callback(DJPRESS_HEADER, valid_content_transformer)
    assert is_valid is False
    assert "Callback requires 1 parameters, but hook only provides 0" in msg

    is_valid, msg = _validate_hook_callback(hook_no_protocol, valid_content_transformer)
    assert is_valid is False
    assert "No protocol defined for hook my_hook" in msg

    is_valid, msg = _validate_hook_callback(PRE_RENDER_CONTENT, None)  # type: ignore
    assert is_valid is False
    assert "Callback is not callable" in msg

    is_valid, msg = _validate_hook_callback(PRE_RENDER_CONTENT, invalid_content_transformer)
    assert is_valid is False
    assert "Parameter type mismatch" in msg

    is_valid, msg = _validate_hook_callback(BAD_HOOK, callback_for_bad_protocol)
    assert is_valid is False
    assert "Signature validation error" in msg


def test_load_plugins_none(registry):
    """Test successful loading of plugins with valid hooks."""

    assert registry._loaded is False
    registry.load_plugins()

    assert registry._loaded is False
    assert len(registry.plugins) == 0
    assert not registry.plugin_errors

    # Load again should exit early
    registry._loaded = True
    assert registry.load_plugins() is None


def test_load_plugins_not_exist(registry, settings, caplog):
    """Test successful loading of plugins with valid hooks."""
    caplog.set_level("WARNING")
    settings.DJPRESS_SETTINGS["PLUGINS"] = ["do_not_exist"]
    settings.DJPRESS_SETTINGS["PLUGIN_SETTINGS"] = {}

    assert registry.load_plugins() is None
    assert "Could not load plugin: 'do_not_exist'" in caplog.text
    assert "Tried both custom path and standard plugin.py location" in caplog.text
    assert "Failed to load plugin: 'do_not_exist'" in caplog.text


def test_load_plugins_exists(registry, settings, caplog, tmp_path):
    """Test successful loading of plugins with valid hooks."""
    caplog.set_level("WARNING")

    # Create a temporary plugin package
    plugin_dir = tmp_path / "test_load_plugins_exists"
    plugin_dir.mkdir()
    (plugin_dir / "__init__.py").write_text("")
    (plugin_dir / "plugin.py").write_text("""
from djpress.plugins import DJPressPlugin
from djpress.plugins.hook_registry import (
    POST_RENDER_CONTENT,
    PRE_RENDER_CONTENT,
)
class TestPlugin(DJPressPlugin):
    name = "test_plugin"
    hooks = [
        (PRE_RENDER_CONTENT, "add_prefix"),
        (POST_RENDER_CONTENT, "add_suffix"),
    ]

    def add_prefix(self, content: str) -> str:
        return f"prefixed_{content}"

    def add_suffix(self, content: str) -> str:
        return f"{content}_suffixed"
""")

    # Add to Python path and try to import
    import sys

    sys.path.insert(0, str(tmp_path))

    settings.DJPRESS_SETTINGS["PLUGINS"] = ["test_load_plugins_exists.plugin.TestPlugin"]

    registry.load_plugins()

    assert registry._loaded is True
    assert len(registry.plugins) == 1
    assert not registry.plugin_errors


def test_load_plugins_non_iterable_hooks(registry, settings, caplog, tmp_path):
    """Test successful loading of plugins with valid hooks."""
    assert len(registry.plugins) == 0
    caplog.set_level("WARNING")

    # Create a temporary plugin package
    plugin_dir = tmp_path / "test_load_plugins_non_iterable_hooks"
    plugin_dir.mkdir()
    (plugin_dir / "__init__.py").write_text("")
    (plugin_dir / "plugin.py").write_text("""
from djpress.plugins import DJPressPlugin
from djpress.plugins.hook_registry import PRE_RENDER_CONTENT

class TestPlugin(DJPressPlugin):
    name = "test_plugin"
    hooks = (PRE_RENDER_CONTENT, "add_prefix")

    def add_prefix(self, content: str) -> str:
        return f"prefixed_{content}"

    def add_suffix(self, content: str) -> str:
        return f"{content}_suffixed"
""")

    # Add to Python path and try to import
    import sys

    sys.path.insert(0, str(tmp_path))

    settings.DJPRESS_SETTINGS["PLUGINS"] = ["test_load_plugins_non_iterable_hooks.plugin.TestPlugin"]

    registry.load_plugins()

    assert registry._loaded is True
    assert len(registry.plugins) == 0
    assert (
        f"Plugin 'test_load_plugins_non_iterable_hooks.plugin.TestPlugin' has a non-iterable 'hooks' attribute"
        in caplog.text
    )


def test_load_plugins_no_name(registry, settings, caplog, tmp_path):
    """Test successful loading of plugins with valid hooks."""
    assert len(registry.plugins) == 0
    caplog.set_level("WARNING")

    # Create a temporary plugin package
    plugin_dir = tmp_path / "test_load_plugins_no_name"
    plugin_dir.mkdir()
    (plugin_dir / "__init__.py").write_text("")
    (plugin_dir / "plugin.py").write_text("""
from djpress.plugins import DJPressPlugin
from djpress.plugins.hook_registry import PRE_RENDER_CONTENT

class TestPlugin(DJPressPlugin):
    hooks = (PRE_RENDER_CONTENT, "add_prefix")

    def add_prefix(self, content: str) -> str:
        return f"prefixed_{content}"

    def add_suffix(self, content: str) -> str:
        return f"{content}_suffixed"
""")

    # Add to Python path and try to import
    import sys

    sys.path.insert(0, str(tmp_path))

    settings.DJPRESS_SETTINGS["PLUGINS"] = ["test_load_plugins_no_name.plugin.TestPlugin"]

    registry.load_plugins()

    assert registry._loaded is True
    assert len(registry.plugins) == 0
    assert f"Error initializing plugin '<class 'test_load_plugins_no_name.plugin.TestPlugin'>'" in caplog.text


def test_register_hook_success(registry, content_transformer_plugin):
    """Test successful registration of a valid hook and a plugin's callback."""

    registry.register_hook(PRE_RENDER_CONTENT, content_transformer_plugin.add_prefix)

    assert PRE_RENDER_CONTENT in registry.hooks
    assert registry.hooks[PRE_RENDER_CONTENT] == [content_transformer_plugin.add_prefix]
    assert not registry.plugin_errors

    registry.register_hook(PRE_RENDER_CONTENT, content_transformer_plugin.add_suffix)

    assert PRE_RENDER_CONTENT in registry.hooks
    assert registry.hooks[PRE_RENDER_CONTENT] == [
        content_transformer_plugin.add_prefix,
        content_transformer_plugin.add_suffix,
    ]
    assert not registry.plugin_errors


def test_register_hook_fail_no_name(registry, caplog):
    """Test successful registration of a valid hook and callback."""
    caplog.set_level("WARNING")

    def test_handler(callback, value) -> object:
        return value

    class TestProtocol(Protocol):
        handler = test_handler

        def __call__(self, content: str) -> str: ...

    def test_callback(content: str) -> str:
        return content

    NO_NAME_HOOK = _Hook(name=None, protocol=TestProtocol)  # type: ignore
    registry.register_hook(NO_NAME_HOOK, test_callback)
    assert NO_NAME_HOOK not in registry.hooks
    assert "Must be a _Hook object" in caplog.text

    NO_NAME_HOOK = _Hook(name="Test", protocol="TestProtocol")  # type: ignore
    registry.register_hook(NO_NAME_HOOK, test_callback)
    assert NO_NAME_HOOK not in registry.hooks
    assert "Must be a _Hook object" in caplog.text


def test_bad_hook_run(registry):
    with pytest.raises(TypeError, match="Invalid hook: 'foobar'. Must be a valid _Hook object."):
        registry.run_hook("foobar")


def test_hook_not_registered(registry):
    class TestProtocol(Protocol):
        def __call__(self, content: str) -> str: ...

    NEW_HOOK = _Hook(name="new_hook", protocol=TestProtocol)

    assert NEW_HOOK not in registry.hooks
    assert registry.run_hook(NEW_HOOK, "test") == "test"


def test_run_hook_no_handler(registry):
    class TestProtocol(Protocol):
        def __call__(self, content: str) -> str: ...

    def test_callback(content: str) -> str:
        return content

    NEW_HOOK = _Hook(name="new_hook", protocol=TestProtocol)

    registry.register_hook(NEW_HOOK, test_callback)
    with pytest.raises(RuntimeError):
        registry.run_hook(NEW_HOOK, "test")


def test_run_hook_success(registry, caplog):
    """Test successful run of a valid hook and callback."""
    caplog.set_level("WARNING")

    def test_handler(callback, value) -> object:
        return value

    class TestProtocol(Protocol):
        handler = test_handler

        def __call__(self, content: str) -> str: ...

    def test_callback(content: str) -> str:
        return content

    NEW_HOOK = _Hook(name="test_hook", protocol=TestProtocol)
    registry.register_hook(NEW_HOOK, test_callback)

    assert registry.run_hook(NEW_HOOK, "test") == "test"


def test_success_run_content_transformer(registry, content_transformer_plugin):
    """Test running a content transformer hook."""
    registry.register_hook(PRE_RENDER_CONTENT, content_transformer_plugin.add_prefix)

    result = registry.run_hook(PRE_RENDER_CONTENT, "content")
    assert result == "prefixed_content"


def test_error_run_content_transformer(registry, caplog):
    """Test running a failed content transformer hook.

    This should return the original content.
    """
    caplog.set_level(logging.WARNING)

    def callback(content: str) -> str:
        raise RuntimeError("This is a test error")

    registry.register_hook(PRE_RENDER_CONTENT, callback)

    result = registry.run_hook(PRE_RENDER_CONTENT, "content")
    assert result == "content"
    assert "Error running callback" in caplog.text
    assert "Callback skipped" in caplog.text
    assert "This is a test error" in caplog.text


def test_success_run_content_provider(registry, content_provider_plugin):
    """Test running a content provider hook."""
    registry.register_hook(DJPRESS_HEADER, content_provider_plugin.add_header)

    result = registry.run_hook(DJPRESS_HEADER)
    assert result == "header"


def test_multiple_content_providers(registry):
    """Test multiple content providers are concatenated."""

    def provider1():
        return "one"

    def provider2():
        return "two"

    registry.register_hook(DJPRESS_HEADER, provider1)
    registry.register_hook(DJPRESS_HEADER, provider2)

    result = registry.run_hook(DJPRESS_HEADER)
    assert result == "onetwo"


def test_error_run_content_provider(registry, caplog):
    """Test running a failed content provider hook.

    This should return an empty string.
    """
    caplog.set_level(logging.WARNING)

    def callback() -> str:
        raise RuntimeError("This is a test error")

    registry.register_hook(DJPRESS_HEADER, callback)

    result = registry.run_hook(DJPRESS_HEADER)
    assert result == ""
    assert "Error running callback" in caplog.text
    assert "Callback skipped" in caplog.text
    assert "This is a test error" in caplog.text


@pytest.mark.django_db
def test_success_run_object_provider(registry, object_provider_plugin, test_post1):
    """Test running a object provider hook."""
    registry.register_hook(POST_SAVE_POST, object_provider_plugin.do_nothing)
    assert POST_SAVE_POST in registry.hooks
    assert not registry.plugin_errors

    result = registry.run_hook(POST_SAVE_POST, test_post1)
    assert result is None


@pytest.mark.django_db
def test_error_run_object_provider(registry, test_post1, caplog):
    """Test running a failed object provider hook.

    This should return None since it is an Action hook.
    """
    caplog.set_level(logging.WARNING)

    def callback(post: "Post") -> object:
        raise RuntimeError("This is a test error")

    registry.register_hook(POST_SAVE_POST, callback)

    result = registry.run_hook(POST_SAVE_POST, test_post1)
    assert result is None
    assert "Error running callback" in caplog.text
    assert "Callback skipped" in caplog.text
    assert "This is a test error" in caplog.text


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


@pytest.mark.django_db
def test_success_run_search_provider(registry, test_post1, test_post2):
    """Test running a search provider hook."""

    def search_callback(query: str):
        return Post.objects.filter(title__icontains=query)

    registry.register_hook(SEARCH_CONTENT, search_callback)

    result = registry.run_hook(SEARCH_CONTENT, "test")
    assert result.count() >= 1


@pytest.mark.django_db
def test_error_run_search_provider(registry, caplog):
    """Test running a failed search provider hook.

    This should return the previous value.
    """
    caplog.set_level(logging.WARNING)

    def callback(query: str):
        raise RuntimeError("This is a test error")

    registry.register_hook(SEARCH_CONTENT, callback)

    result = registry.run_hook(SEARCH_CONTENT, "test")
    assert result == "test"
    assert "Error running callback" in caplog.text
    assert "Callback skipped" in caplog.text
    assert "This is a test error" in caplog.text


@pytest.mark.django_db
def test_search_provider_returns_non_queryset(registry, caplog):
    """Test search provider that returns non-QuerySet.

    This should return the previous value.
    """
    caplog.set_level(logging.DEBUG)

    def callback(query: str):
        return ["not", "a", "queryset"]

    registry.register_hook(SEARCH_CONTENT, callback)

    result = registry.run_hook(SEARCH_CONTENT, "test")
    assert result == "test"
    assert "did not return a QuerySet" in caplog.text


@pytest.mark.django_db
def test_search_provider_returns_queryset(registry, caplog, test_post1):
    """If the value is a queryset, we just return it."""
    caplog.set_level(logging.DEBUG)

    previous_result = Post.objects.filter(title__icontains="test")

    def callback1(query: str):
        return Post.objects.filter(title__icontains=query)

    def callback2(query: str):
        return Post.objects.filter(title__icontains=query)

    registry.register_hook(SEARCH_CONTENT, callback1)
    registry.register_hook(SEARCH_CONTENT, callback2)

    result = registry.run_hook(SEARCH_CONTENT, "test")
    assert result.count() == 1
    assert "not attempting to search again" in caplog.text


def test_validate_hook_callback_with_class_annotation():
    """Test validation when the callback uses the actual class type instead of string representation."""

    def callback_with_class(post: Post) -> Post:
        return post

    is_valid, msg = _validate_hook_callback(POST_SAVE_POST, callback_with_class)
    assert is_valid is True
    assert msg == ""


def test_validate_hook_callback_with_callable_object():
    """Test validation when the callback is a callable class instance."""

    class ContentFilter:
        def __call__(self, content: str) -> str:
            return content

    is_valid, msg = _validate_hook_callback(PRE_RENDER_CONTENT, ContentFilter())
    assert is_valid is True
    assert msg == ""


def test_validate_hook_callback_with_optional_params():
    """Test validation when the callback has optional parameters with defaults."""

    def callback_with_defaults(content: str, format_type: str = "html") -> str:
        return content

    is_valid, msg = _validate_hook_callback(PRE_RENDER_CONTENT, callback_with_defaults)
    assert is_valid is True
    assert msg == ""


def test_validate_hook_callback_with_object_annotation():
    """Test validation when the callback accepts any object (type hint 'object')."""

    def callback_with_object(post: object) -> None:
        pass

    is_valid, msg = _validate_hook_callback(POST_SAVE_POST, callback_with_object)
    assert is_valid is True
    assert msg == ""


def test_import_plugin_class_chains_exceptions(registry):
    """Test that _import_plugin_class chains the original exception when loading fails."""
    with pytest.raises(ImproperlyConfigured) as exc_info:
        registry._import_plugin_class("non_existent_module")

    assert exc_info.value.__cause__ is not None
    assert isinstance(exc_info.value.__cause__, ImportError)
    assert "non_existent_module" in str(exc_info.value.__cause__)


def test_load_plugins_atomic_rollback(registry, settings, caplog, tmp_path):
    """Test that if a plugin has multiple hooks and one fails with AttributeError, all are rolled back."""
    caplog.set_level("WARNING")

    # Create a temporary plugin package
    plugin_dir = tmp_path / "test_load_plugins_atomic_rollback"
    plugin_dir.mkdir()
    (plugin_dir / "__init__.py").write_text("")
    (plugin_dir / "plugin.py").write_text("""
from djpress.plugins import DJPressPlugin
from djpress.plugins.hook_registry import (
    PRE_RENDER_CONTENT,
    POST_RENDER_CONTENT,
)
class TestPlugin(DJPressPlugin):
    name = "test_plugin_atomic"
    hooks = [
        (PRE_RENDER_CONTENT, "add_prefix"),
        (POST_RENDER_CONTENT, "add_suffix"),  # This method is missing!
    ]

    def add_prefix(self, content: str) -> str:
        return f"prefixed_{content}"
""")

    # Add to Python path and try to import
    import sys

    sys.path.insert(0, str(tmp_path))

    settings.DJPRESS_SETTINGS["PLUGINS"] = ["test_load_plugins_atomic_rollback.plugin.TestPlugin"]

    registry.load_plugins()

    assert registry._loaded is True
    assert len(registry.plugins) == 0
    # The first hook (PRE_RENDER_CONTENT) should NOT be registered
    assert PRE_RENDER_CONTENT not in registry.hooks or not registry.hooks[PRE_RENDER_CONTENT]
    assert "Failed to load plugin" in caplog.text


def test_load_plugins_atomic_rollback_validation(registry, settings, caplog, tmp_path):
    """Test that if a plugin has multiple hooks and one fails validation, all are rolled back."""
    caplog.set_level("WARNING")

    # Create a temporary plugin package
    plugin_dir = tmp_path / "test_load_plugins_atomic_rollback_validation"
    plugin_dir.mkdir()
    (plugin_dir / "__init__.py").write_text("")
    (plugin_dir / "plugin.py").write_text("""
from djpress.plugins import DJPressPlugin
from djpress.plugins.hook_registry import (
    PRE_RENDER_CONTENT,
    POST_RENDER_CONTENT,
)
class TestPlugin(DJPressPlugin):
    name = "test_plugin_atomic_val"
    hooks = [
        (PRE_RENDER_CONTENT, "add_prefix"),
        (POST_RENDER_CONTENT, "add_suffix_invalid"),  # This method has invalid signature!
    ]

    def add_prefix(self, content: str) -> str:
        return f"prefixed_{content}"

    def add_suffix_invalid(self, content: str, extra: int) -> str:
        return f"{content}_suffixed"
""")

    # Add to Python path and try to import
    import sys

    sys.path.insert(0, str(tmp_path))

    settings.DJPRESS_SETTINGS["PLUGINS"] = ["test_load_plugins_atomic_rollback_validation.plugin.TestPlugin"]

    registry.load_plugins()

    assert registry._loaded is True
    assert len(registry.plugins) == 0
    # The first hook (PRE_RENDER_CONTENT) should NOT be registered
    assert PRE_RENDER_CONTENT not in registry.hooks or not registry.hooks[PRE_RENDER_CONTENT]
    assert "Failed to load plugin" in caplog.text


def test_plugin_config_property_alias(settings):
    """Test that the plugin.config property is an alias for plugin.settings."""
    settings.DJPRESS_SETTINGS["PLUGIN_SETTINGS"] = {"alias_plugin": {"hello": "world"}}
    plugin = DJPressPlugin()
    plugin.name = "alias_plugin"
    assert plugin.config == {"hello": "world"}
    assert plugin.config is plugin.settings


class CustomTestRegistry(PluginRegistry):
    """A custom PluginRegistry class for testing purposes."""

    def __init__(self):
        super().__init__()
        self.custom_initialized = True


def test_lazy_registry_custom_class(settings):
    """Test that setting PLUGIN_REGISTRY_CLASS loads the custom class."""
    settings.DJPRESS_SETTINGS["PLUGIN_REGISTRY_CLASS"] = "tests.test_plugins.CustomTestRegistry"

    from djpress.plugins.plugin_registry import _get_plugin_registry

    custom_registry = _get_plugin_registry()
    assert isinstance(custom_registry, CustomTestRegistry)
    assert getattr(custom_registry, "custom_initialized", False) is True


def test_lazy_registry_custom_class_fallback_on_error(settings, caplog):
    """Test that setting PLUGIN_REGISTRY_CLASS to an invalid path falls back to the default class."""
    caplog.set_level("WARNING")
    settings.DJPRESS_SETTINGS["PLUGIN_REGISTRY_CLASS"] = "invalid.module.Path"

    from djpress.plugins.plugin_registry import _get_plugin_registry

    fallback_registry = _get_plugin_registry()
    assert isinstance(fallback_registry, PluginRegistry)
    assert not isinstance(fallback_registry, CustomTestRegistry)
    assert "Could not load custom plugin registry class" in caplog.text


def test_dynamic_plugin_settings(settings):
    """Test that plugin settings are retrieved dynamically."""
    settings.DJPRESS_SETTINGS["PLUGIN_SETTINGS"] = {"dynamic_plugin": {"key": "value"}}

    plugin = DJPressPlugin()
    plugin.name = "dynamic_plugin"
    assert plugin.settings == {"key": "value"}

    # Dynamic settings change
    settings.DJPRESS_SETTINGS["PLUGIN_SETTINGS"]["dynamic_plugin"]["key"] = "new_value"
    assert plugin.settings == {"key": "new_value"}

    # Dynamic settings change of whole dictionary
    settings.DJPRESS_SETTINGS["PLUGIN_SETTINGS"] = {"dynamic_plugin": {"another_key": "another_value"}}
    assert plugin.settings == {"another_key": "another_value"}

    # Fallback to empty dict if PLUGIN_SETTINGS does not exist or is not a dict
    del settings.DJPRESS_SETTINGS["PLUGIN_SETTINGS"]
    assert plugin.settings == {}

    settings.DJPRESS_SETTINGS["PLUGIN_SETTINGS"] = "not_a_dict"
    assert plugin.settings == {}


def test_broken_plugin_constructor_raises_error(registry):
    """Test that a plugin expecting arguments in __init__ fails to instantiate with ImproperlyConfigured."""

    class BrokenPlugin(DJPressPlugin):
        name = "broken_plugin"

        def __init__(self, required_arg):
            super().__init__()
            self.required_arg = required_arg

    with pytest.raises(ImproperlyConfigured) as exc_info:
        registry._instantiate_plugin(BrokenPlugin)
    assert "Error initializing plugin" in str(exc_info.value)


def test_dynamic_plugin_settings_non_dict_fallback():
    """Test that dynamic settings lookup returns empty dict if PLUGIN_SETTINGS is not a dict."""
    plugin = DJPressPlugin()
    plugin.name = "dynamic_plugin"
    with patch("djpress.plugins.base_plugin.djpress_settings") as mock_settings:
        mock_settings.PLUGIN_SETTINGS = "not_a_dict_raw"
        assert plugin.settings == {}


@pytest.mark.django_db
def test_plugin_dynamic_enabling_and_disabling(registry, settings):
    """Test dynamic enabling and disabling of plugins with defaults, file settings, and DB settings."""
    from djpress.models.setting import Setting
    from djpress.conf import settings as djpress_settings

    # Plugin A: default is disabled
    class PluginA(DJPressPlugin):
        name = "plugin_a"
        hooks = [(PRE_RENDER_CONTENT, "add_prefix")]

        def add_prefix(self, content: str) -> str:
            return f"A_{content}"

    # Plugin B: default is disabled
    class PluginB(DJPressPlugin):
        name = "plugin_b"
        hooks = [(PRE_RENDER_CONTENT, "add_prefix")]

        def add_prefix(self, content: str) -> str:
            return f"B_{content}"

    # Instantiate plugins
    plugin_a = PluginA()
    plugin_b = PluginB()

    # Register hooks
    registry.register_hook(PRE_RENDER_CONTENT, plugin_a.add_prefix)
    registry.register_hook(PRE_RENDER_CONTENT, plugin_b.add_prefix)

    # 1. Test Default Fallback
    # Both plugins are disabled by default.
    # So run_hook should execute neither hook and return the original string.
    res1 = registry.run_hook(PRE_RENDER_CONTENT, "test")
    assert res1 == "test"

    # 2. Test File-based settings overrides
    # Enable Plugin A, Disable Plugin B in file settings.
    settings.DJPRESS_SETTINGS["PLUGIN_SETTINGS"] = {
        "plugin_a": {"enabled": True},
        "plugin_b": {"enabled": False},
    }

    # Verify: Plugin A should run, Plugin B should be skipped.
    res2 = registry.run_hook(PRE_RENDER_CONTENT, "test")
    assert res2 == "A_test"

    # 3. Test Database-backed settings overrides
    # Enable database settings lookups in django settings.
    settings.DJPRESS_SETTINGS = {
        "DATABASE_SETTINGS_ENABLED": True,
    }
    djpress_settings.clear_request_cache()

    # In database, enable Plugin B and disable Plugin A.
    Setting.objects.create(
        key="PLUGIN_SETTINGS",
        value={
            "plugin_a": {"enabled": False},
            "plugin_b": {"enabled": True},
        },
    )
    djpress_settings.clear_request_cache()

    # Verify: Plugin B should run, Plugin A should be skipped.
    res3 = registry.run_hook(PRE_RENDER_CONTENT, "test")
    assert res3 == "B_test"

    # 4. Test Dynamic Runtime Updates (Toggling settings dynamically)
    # Update the database setting to enable both Plugin A and Plugin B
    db_setting = Setting.objects.get(key="PLUGIN_SETTINGS")
    db_setting.value = {
        "plugin_a": {"enabled": True},
        "plugin_b": {"enabled": True},
    }
    db_setting.save()
    djpress_settings.clear_request_cache()

    # Verify: both Plugin A and Plugin B run in a waterfall chain (A then B).
    res4 = registry.run_hook(PRE_RENDER_CONTENT, "test")
    assert res4 == "B_A_test"


@pytest.mark.django_db
def test_action_hook_execution_isolation(registry, test_post1):
    """Test that action hook callbacks are executed independently and errors are isolated."""
    from djpress.plugins.hook_registry import HookType, POST_SAVE_POST

    assert POST_SAVE_POST.hook_type == HookType.ACTION

    execution_order = []

    def callback_success_1(post):
        execution_order.append("success_1")
        return "some_value"

    def callback_failing(post):
        execution_order.append("failing")
        raise ValueError("Error in action callback")

    def callback_success_2(post):
        execution_order.append("success_2")
        return "another_value"

    registry.register_hook(POST_SAVE_POST, callback_success_1)
    registry.register_hook(POST_SAVE_POST, callback_failing)
    registry.register_hook(POST_SAVE_POST, callback_success_2)

    result = registry.run_hook(POST_SAVE_POST, test_post1)

    # All three callbacks should have executed (even after failure in the second)
    assert execution_order == ["success_1", "failing", "success_2"]

    # Return value of run_hook should be None
    assert result is None


@pytest.mark.django_db
def test_action_hook_disabled(registry, test_post1, settings):
    """Test that disabled action plugin callbacks are skipped in run_hook."""
    from djpress.plugins.hook_registry import POST_SAVE_POST

    class DummyActionPlugin(DJPressPlugin):
        name = "dummy_action_plugin"
        hooks = [(POST_SAVE_POST, "on_save")]

        def __init__(self):
            super().__init__()
            self.called = False

        def on_save(self, post):
            self.called = True

    plugin = DummyActionPlugin()
    registry.register_hook(POST_SAVE_POST, plugin.on_save)

    # By default it's disabled
    settings.DJPRESS_SETTINGS["PLUGIN_SETTINGS"] = {"dummy_action_plugin": {"enabled": False}}
    result = registry.run_hook(POST_SAVE_POST, test_post1)
    assert not plugin.called
    assert result is None

    # Enable it
    settings.DJPRESS_SETTINGS["PLUGIN_SETTINGS"] = {"dummy_action_plugin": {"enabled": True}}
    result = registry.run_hook(POST_SAVE_POST, test_post1)
    assert plugin.called
    assert result is None


def test_action_hook_handler_exception(registry, caplog):
    """Test that run_hook catches and logs exceptions raised by the protocol handler for actions."""
    from djpress.plugins.hook_registry import HookType, _Hook
    import logging

    caplog.set_level(logging.WARNING)

    class BadProtocol:
        @staticmethod
        def handler(callback, value):
            raise RuntimeError("Handler error")

        def __call__(self):
            pass

    BAD_ACTION_HOOK = _Hook("bad_action_hook", BadProtocol, hook_type=HookType.ACTION)

    def dummy_callback():
        pass

    registry.register_hook(BAD_ACTION_HOOK, dummy_callback)

    result = registry.run_hook(BAD_ACTION_HOOK, "test")
    assert result is None
    assert "Error running action callback" in caplog.text
    assert "Handler error" in caplog.text
