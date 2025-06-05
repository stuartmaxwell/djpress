"""Plugin system for DJ Press."""

import logging
from collections.abc import Callable
from enum import Enum
from typing import TYPE_CHECKING, Any

from django.utils.module_loading import import_string

from djpress.conf import settings as djpress_settings
from djpress.plugins.hook_registry import Hooks

if TYPE_CHECKING:
    from djpress.plugins.base_plugin import DJPressPlugin

logger = logging.getLogger(__name__)


class PluginRegistry:
    """A registry for plugins.

    Handles plugin discovery, loading, and hook management.
    """

    def __init__(self) -> None:
        """Initialize the registry."""
        self.plugins = []
        self.hooks = {}
        self._loaded = False
        # Any errors encountered during plugin loading will be stored here for the Django checks system to report.
        self.plugin_errors = []

    def register_hook(self, hook_name: Hooks | str, callback: Callable) -> None:
        """Register a callback function for a specific hook.

        Args:
            hook_name (Hooks | str): The name of the hook - this can be referenced either as the plain text name of
                the hook (e.g. `"pre_render_content"`) or as a Hooks enum member (e.g. `Hooks.PRE_RENDER_CONTENT`).
            callback (callable): The function to call when the hook is triggered.

        Raises:
            TypeError: If hook_name is not a Hooks enum member.
        """
        # Convert string to Enum if needed, and log a warning if invalid
        if isinstance(hook_name, str):
            try:
                hook_name = Hooks(hook_name)
            except ValueError:
                # Not a valid hook name, return early
                msg = f"Invalid hook str name: {hook_name}. Hook not registered by callback."
                self.plugin_errors.append(msg)
                logger.warning(msg)
                return

        # If it's already an enum, check if it's valid
        if isinstance(hook_name, Enum) and not isinstance(hook_name, Hooks):
            # Not a valid hook enum, return early
            msg = f"Invalid hook enum: {hook_name}. Hook not registered by callback."
            self.plugin_errors.append(msg)
            logger.warning(msg)
            return

        # If the hook is not already registered, create a new list for it in the hooks dictionary
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []

        # Append the callback to the list for this hook
        self.hooks[hook_name].append(callback)

    def run_hook(self, hook_name: Hooks, value: Any = None) -> Any:  # noqa: ANN401
        """Run all registered callbacks for a given hook.

        Args:
            hook_name (Hooks): The name of the hook to run, this should be in the form of a Hooks enum member.
            value: The value to be modified by the callbacks.

        Returns:
            The value after all callbacks have been run.

        Raises:
            TypeError: If hook_name is not a Hooks enum member.
        """
        if not isinstance(hook_name, Hooks):
            msg = f"hook_name must be a Hooks enum member, got {type(hook_name)}"
            logger.warning(msg)

        # If there are no plugins loaded, exit early
        if not self.plugins:
            return value

        if hook_name in self.hooks:
            for callback in self.hooks[hook_name]:
                # Ruff warns us about performance issues running a try/except block in a loop, but I think this is
                # acceptable since there won't be many hooks, and we don't want one crashing plugin to affect all the
                # plugins. With this approach, if one fails, the `value` won't be modified and we'll continue to the
                # next one.
                try:
                    callback_value = callback(value)
                    value = callback_value
                except Exception:  # noqa: BLE001, PERF203
                    # Log the error but continue with the next callback
                    msg = (
                        f"Error running callback {callback.__name__} for hook: {hook_name.name}. "
                        f"The callback will be skipped."
                    )
                    logger.warning(msg, exc_info=True)
                    # Continue with the next callback
                    continue

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

        # Clear previous errors to avoid duplicates on reload
        self.plugin_errors.clear()

        plugin_names = djpress_settings.PLUGINS
        if not plugin_names:
            return
        if not isinstance(plugin_names, list):  # pragma: no cover
            msg = f"Expected PLUGINS to be a list, got {type(plugin_names).__name__}"
            raise TypeError(msg)

        plugin_settings = djpress_settings.PLUGIN_SETTINGS
        if not plugin_settings:
            plugin_settings = {}
        if not isinstance(plugin_settings, dict):  # pragma: no cover
            msg = f"Expected PLUGIN_SETTINGS to be a dict, got {type(plugin_settings).__name__}"
            raise TypeError(msg)

        try:
            for plugin_path in plugin_names:
                plugin_class = self._import_plugin_class(plugin_path)
                plugin = self._instantiate_plugin(plugin_class, plugin_path, plugin_settings)
                self.plugins.append(plugin)

            self._loaded = True
        except Exception as exc:  # noqa: BLE001
            msg = f"Failed to load plugins: {exc}"
            self.plugin_errors.append(msg)
            logger.warning(msg)

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

    def _instantiate_plugin(
        self,
        plugin_class: type,
        plugin_path: str,
        plugin_settings: dict,
    ) -> "DJPressPlugin":
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

            # Set up the plugin - this is where the hooks are registered
            plugin.setup(self)

        except Exception as exc:
            from django.core.exceptions import ImproperlyConfigured

            msg = f"Error initializing plugin '{plugin_path}': {exc!s}"
            raise ImproperlyConfigured(msg) from exc

        else:
            return plugin


# Instantiate the global plugin registry
registry = PluginRegistry()
