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
    DJ_FOOTER,
    DJ_HEADER,
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
        (DJ_HEADER, "render_header"),
        (DJ_FOOTER, "render_footer"),
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

    def __init__(self, settings: dict):
        super().__init__(settings)
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

    def __init__(self, settings: dict):
        # This will raise an exception
        super().__init__(settings)
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
    assert "Expected 1 parameters, got 2" in msg

    is_valid, msg = _validate_hook_callback(DJ_HEADER, invalid_no_args)
    assert is_valid is True

    is_valid, msg = _validate_hook_callback(DJ_HEADER, valid_content_transformer)
    assert is_valid is False
    assert "Expected 0 parameters, got 1" in msg

    is_valid, msg = _validate_hook_callback(hook_no_protocol, valid_content_transformer)
    assert is_valid is False
    assert "No protocol defined for hook my_hook" in msg

    is_valid, msg = _validate_hook_callback(PRE_RENDER_CONTENT, None)  # type: ignore
    assert is_valid is False
    assert "Callback is expected to be a method or function" in msg

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
    registry.register_hook(DJ_HEADER, content_provider_plugin.add_header)

    result = registry.run_hook(DJ_HEADER)
    assert result == "header"


def test_error_run_content_provider(registry, caplog):
    """Test running a failed content provider hook.

    This should return an empty string.
    """
    caplog.set_level(logging.WARNING)

    def callback() -> str:
        raise RuntimeError("This is a test error")

    registry.register_hook(DJ_HEADER, callback)

    result = registry.run_hook(DJ_HEADER)
    assert result == ""
    assert "Error running callback" in caplog.text
    assert "Callback skipped" in caplog.text
    assert "This is a test error" in caplog.text


@pytest.mark.django_db
def test_success_run_object_provider(registry, object_provider_plugin, test_post1):
    """Test running a object provider hook."""
    registry.register_hook(POST_SAVE_POST, object_provider_plugin.do_nothing)

    result = registry.run_hook(POST_SAVE_POST, test_post1)
    assert result == test_post1


@pytest.mark.django_db
def test_error_run_object_provider(registry, test_post1, caplog):
    """Test running a failed object provider hook.

    This should return the original post.
    """
    caplog.set_level(logging.WARNING)

    def callback(post: "Post") -> object:
        raise RuntimeError("This is a test error")

    registry.register_hook(POST_SAVE_POST, callback)

    result = registry.run_hook(POST_SAVE_POST, test_post1)
    assert result == test_post1
    assert "Error running callback" in caplog.text
    assert "Callback skipped" in caplog.text
    assert "This is a test error" in caplog.text


@pytest.mark.django_db
def test_plugin_storage_interface():
    """Test plugin storage interface methods."""

    class TestPlugin(DJPressPlugin):
        name = "test_plugin"

    plugin = TestPlugin({})

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

    This should return None.
    """
    caplog.set_level(logging.WARNING)

    def callback(query: str):
        raise RuntimeError("This is a test error")

    registry.register_hook(SEARCH_CONTENT, callback)

    result = registry.run_hook(SEARCH_CONTENT, "test")
    assert result is None
    assert "Error running callback" in caplog.text
    assert "Callback skipped" in caplog.text
    assert "This is a test error" in caplog.text


@pytest.mark.django_db
def test_search_provider_returns_non_queryset(registry, caplog):
    """Test search provider that returns non-QuerySet.

    This should return None.
    """
    caplog.set_level(logging.DEBUG)

    def callback(query: str):
        return ["not", "a", "queryset"]

    registry.register_hook(SEARCH_CONTENT, callback)

    result = registry.run_hook(SEARCH_CONTENT, "test")
    assert result is None
    assert "did not return a QuerySet" in caplog.text
