"""Plugin system for DJ Press."""

import contextlib  # Ruff: SIM105
from enum import Enum
from typing import Any

from django.utils.module_loading import import_string

from djpress.conf import settings as djpress_settings


# Hook definitions
class Hooks(Enum):
    """Available hook points in DJ Press."""

    PRE_RENDER_CONTENT = "pre_render_content"
    POST_RENDER_CONTENT = "post_render_content"
    POST_SAVE_POST = "post_save_post"


class PluginRegistry:
    """A registry for plugins.

    Handles plugin discovery, loading, and hook management.
    """

    def __init__(self) -> None:
        """Initialize the registry."""
        self.plugins = []
        self.hooks = {}
        self._loaded = False

    def register_hook(self, hook_name: Hooks | str, callback: callable) -> None:
        """Register a callback function for a specific hook.

        Args:
            hook_name (Hooks | str): The name of the hook - this can be referenced either as the plain text name of
                the hook (e.g. `"pre_render_content"`) or as a Hooks enum member (e.g. `Hooks.PRE_RENDER_CONTENT`).
            callback (callable): The function to call when the hook is triggered.

        Raises:
            TypeError: If hook_name is not a Hooks enum member.
        """
        # Convert string to Enum if needed, and supress error if not possible
        if isinstance(hook_name, str):
            with contextlib.suppress(ValueError):
                hook_name = Hooks(hook_name)

        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        self.hooks[hook_name].append(callback)

    def run_hook(self, hook_name: Hooks, value: Any = None, *args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        """Run all registered callbacks for a given hook.

        Args:
            hook_name (Hooks): The name of the hook to run, this should be in the form of a Hooks enum member.
            value: The value to be modified by the callbacks.
            *args: Additional positional arguments to pass to the callbacks.
            **kwargs: Additional keyword arguments to pass to the callbacks.

        Returns:
            The value after all callbacks have been run.

        Raises:
            TypeError: If hook_name is not a Hooks enum member.
        """
        if not isinstance(hook_name, Hooks):
            msg = f"hook_name must be a Hooks enum member, got {type(hook_name)}"
            raise TypeError(msg)

        if not self._loaded:
            self.load_plugins()

        if hook_name in self.hooks:
            for callback in self.hooks[hook_name]:
                value = callback(value, *args, **kwargs)

        return value

    def load_plugins(self) -> None:
        """Load all plugins.

        Plugins need to be added to the DJPRESS_SETTINGS['PLUGINS'] list.

        Plugins can be added to DJPRESS_SETTINGS['PLUGINS'] in two ways:
        1. Just the package name (e.g., "djpress_example_plugin") which will look for Plugin class in plugin.py
        2. Full path to the plugin class (e.g., "djpress_example_plugin.custom.MyPlugin")
        """
        if self._loaded:
            return

        plugin_names: list = djpress_settings.PLUGINS
        plugin_settings: dict = djpress_settings.PLUGIN_SETTINGS

        for plugin_path in plugin_names:
            plugin_class = self._import_plugin_class(plugin_path)
            plugin = self._instantiate_plugin(plugin_class, plugin_path, plugin_settings)
            self.plugins.append(plugin)

        self._loaded = True

    def _import_plugin_class(self, plugin_path: str) -> type:
        """Import the plugin class from either custom path or standard location.

        Args:
            plugin_path: Either full path to plugin class or just the package name.

        Returns:
            The plugin class.

        Raises:
            ImproperlyConfigured: If plugin cannot be loaded from either location.
        """
        # Try full path first
        try:
            return import_string(plugin_path)
        except ImportError:
            pass

        # Try standard plugin.py location
        try:
            return import_string(f"{plugin_path}.plugin.Plugin")
        except ImportError as exc:
            from django.core.exceptions import ImproperlyConfigured

            msg = (
                f"Could not load plugin '{plugin_path}'. "
                f"Tried both custom path and standard plugin.py location. "
                f"Error: {exc}"
            )
            raise ImproperlyConfigured(msg) from exc

    def _instantiate_plugin(self, plugin_class: type, plugin_path: str, plugin_settings: dict) -> "DJPressPlugin":
        """Create and set up a plugin instance.

        Args:
            plugin_class: The plugin class to instantiate.
            plugin_path: The original plugin path (used for error reporting).
            plugin_settings: Dictionary of settings for all plugins.

        Returns:
            An initialized plugin instance.

        Raises:
            ImproperlyConfigured: If plugin cannot be instantiated or set up.
        """
        try:
            # Get plugin-specific settings
            plugin_name = plugin_class.name if hasattr(plugin_class, "name") else plugin_path
            plugin_config = plugin_settings.get(plugin_name, {})

            # Create plugin instance with optional config
            plugin = plugin_class(config=plugin_config) if plugin_config else plugin_class()

            # Set up the plugin
            plugin.setup(self)

        except Exception as exc:
            from django.core.exceptions import ImproperlyConfigured

            msg = f"Error initializing plugin '{plugin_path}': {exc!s}"
            raise ImproperlyConfigured(msg) from exc

        else:
            return plugin


class DJPressPlugin:
    """Base class for DJ Press plugins."""

    name: str | None = None

    def __init__(self, config: dict | None = None) -> None:
        """Initialize the plugin."""
        if self.name is None:
            msg = "Plugin must define a name"
            raise ValueError(msg)
        self.config = config or {}

    def setup(self, registry: PluginRegistry) -> None:
        """Set up the plugin.

        Args:
            registry (PluginRegistry): The plugin registry.
        """

    def get_data(self) -> dict:
        """Get this plugin's stored data.

        Returns:
            dict: The plugin's stored data, or empty dict if none exists.
        """
        from djpress.models import PluginStorage

        return PluginStorage.objects.get_data(self.name)

    def save_data(self, data: dict) -> None:
        """Save this plugin's data.

        Args:
            data: The data to store for this plugin.
        """
        from djpress.models import PluginStorage

        PluginStorage.objects.save_data(self.name, data)


# Instantiate the global plugin registry
registry = PluginRegistry()
