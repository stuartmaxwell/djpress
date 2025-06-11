"""Plugin system for DJ Press."""

import logging
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from djpress.conf import settings as djpress_settings
from djpress.plugins.hook_registry import (
    _Hook,
    _validate_hook_callback,
)

if TYPE_CHECKING:
    from djpress.plugins.base_plugin import DJPressPlugin

logger = logging.getLogger(__name__)


class PluginRegistry:
    """A registry for plugins.

    Provides three key features:

    1. Load the plugins defined in DJPRESS_SETTINGS['PLUGINS'] into `self.plugins`.
    2. Register hooks and their callbacks into `self.hooks`, ensuring they match the expected protocol.
    3. Run the callbacks for a given hook.
    """

    def __init__(self) -> None:
        """Initialize the registry."""
        self.plugins: list[DJPressPlugin] = []
        self.hooks: dict[_Hook, list[object]] = {}
        self._loaded: bool = False
        self.plugin_errors: list[str] = []

    def load_plugins(self) -> None:
        """Load all plugins.

        Plugins need to be added to the DJPRESS_SETTINGS['PLUGINS'] list.

        Plugins can be added to DJPRESS_SETTINGS['PLUGINS'] in two ways:
        1. Just the package name (e.g., "djpress_example_plugin") which will look for Plugin class in plugin.py
        2. Full path to the plugin class (e.g., "djpress_example_plugin.custom.MyPlugin")
        """
        # If plugins are already loaded, exit.
        if self._loaded:
            return

        # Ensure any previous errors are cleared
        self.plugin_errors.clear()

        # Get the plugin names from the DJPress settings.
        plugin_names = djpress_settings.PLUGINS
        # If there are no plugins, exit.
        if not plugin_names:
            return
        # If plugin names is not a list, log a warning and exit.
        if not isinstance(plugin_names, list):  # pragma: no cover
            msg = f"Expected PLUGINS to be a list, got {type(plugin_names).__name__}"
            self.plugin_errors.append(msg)
            logger.warning(msg)
            return

        # Get the plugin settings from the DJ Press settings.
        plugin_settings = djpress_settings.PLUGIN_SETTINGS
        # If there are no plugin settings, assign an empty dict.
        if not plugin_settings:
            plugin_settings = {}
        # If plugin settings is not a dict, log a warning and exit.
        if not isinstance(plugin_settings, dict):  # pragma: no cover
            msg = f"Expected PLUGIN_SETTINGS to be a dict, got {type(plugin_settings).__name__}"
            self.plugin_errors.append(msg)
            logger.warning(msg)
            return

        # Try to import each plugin and register its hooks.
        for plugin_path in plugin_names:
            try:
                # Get the plugin class.
                plugin_class = self._import_plugin_class(plugin_path)
                # Load the plugin
                plugin = self._instantiate_plugin(plugin_class, plugin_settings)
                # Get the hooks - this should be a list of (hook, method_name) tuples.
                hooks = plugin.hooks
                # And loop through the hooks to try  register them.
                try:
                    for hook, method_name in hooks:
                        callback = getattr(plugin, method_name)
                        self.register_hook(hook, callback)

                    # If we get to this point the plugin has been successfully loaded.
                    self.plugins.append(plugin)
                except TypeError as exc:
                    logger.warning(
                        f"Plugin '{plugin_path}' has a non-iterable 'hooks' attribute: {exc}. "
                        "Skipping hook registration.",
                    )

            except Exception as exc:  # noqa: BLE001, PERF203
                msg = f"Failed to load plugin: '{plugin_path}' {exc}"
                self.plugin_errors.append(msg)
                logger.warning(msg)
        self._loaded = True

    def register_hook(self, hook: "_Hook", callback: Callable[..., Any]) -> None:
        """Register a callback function for a specific hook.

        Args:
            hook: The _Hook object.
            callback: The function to call when the hook is triggered.

        Raises:
            TypeError: If the hook is not a _Hook object.
            TypeError: If the callback does not match the expected protocol.
        """
        # If the hook doesn't have the required attribute typer, log a warning and exit.
        if not isinstance(hook.protocol, object) or not isinstance(hook.name, str):
            msg = f"Invalid hook: '{hook!r}'. Must be a _Hook object."
            self.plugin_errors.append(msg)
            logger.warning(msg)
            return

        # Validate the callback against the hook's protocol.
        is_valid, error = _validate_hook_callback(hook, callback)
        if not is_valid:
            msg = f"Invalid callback signature for hook '{hook.name}': {error}"
            self.plugin_errors.append(msg)
            logger.warning(msg)
            return

        # If this hook has had no callbacks registered yet, initialize an empty list.
        if hook not in self.hooks:
            self.hooks[hook] = []

        # Register the callback for the hooks.
        self.hooks[hook].append(callback)

    def run_hook(self, hook: "_Hook", value: object | None = None) -> object:
        """Run all callbacks for a given hook.

        Args:
            hook: The _Hook object to execute.
            value: Optional value to pass to the hook. The value is returned if received.

        Returns:
            The result of the chained callbacks, or None if no value was received.

        Raises:
            TypeError: If the hook is not a _Hook object.
        """
        # Check that the hook has been defined correctly.
        if not isinstance(hook, _Hook) or not hasattr(hook, "protocol"):
            msg = f"Invalid hook: {hook!r}. Must be a valid _Hook object."
            raise TypeError(msg)

        # Check that the hook has been registered, if not then return the received value.
        if hook not in self.hooks:
            return value

        # Get the handler for the protocol, if it doesn't exist, raise an error.
        protocol = getattr(hook, "protocol", None)
        handler = getattr(protocol, "handler", None)
        if not handler:
            msg = f"No handler found for hook '{hook.name}' (protocol: '{protocol}')"
            raise RuntimeError(msg)

        # Get the callbacks for the hook.
        callbacks = self.hooks[hook]

        # Loop through the callbacks, updating the value.
        for callback in callbacks:
            value = handler(callback, value)

        return value

    def _import_plugin_class(self, plugin_path: str) -> type:
        """Import the plugin class from either custom path or standard location.

        Args:
            plugin_path: Either full path to plugin class or just the package name.

        Returns:
            The plugin class.

        Raises:
            ImproperlyConfigured: If plugin cannot be loaded from either location.
        """
        try:
            return import_string(plugin_path)
        except ImportError:
            pass

        try:
            return import_string(f"{plugin_path}.plugin.Plugin")
        except ImportError as exc:
            from django.core.exceptions import ImproperlyConfigured

            msg = (
                f"Could not load plugin: '{plugin_path}'. "
                f"Tried both custom path and standard plugin.py location. "
                f"Error: {exc}"
            )
            self.plugin_errors.append(msg)
            logger.warning(msg)
            raise ImproperlyConfigured(msg) from exc

    def _instantiate_plugin(
        self,
        plugin_class: type,
        plugin_settings: dict,
    ) -> "DJPressPlugin":
        """Create and set up a plugin instance.

        Args:
            plugin_class: The plugin class to instantiate.
            plugin_settings: Dictionary of settings for all plugins.

        Returns:
            An initialized plugin instance.

        Raises:
            ImproperlyConfigured: If plugin cannot be instantiated or set up.
        """
        try:
            # If there's no name, this will raise an error.
            plugin_name = plugin_class.name
            # Get the plugin's settings from the plugin_settimgs or an empty dict.
            this_plugin_settings = plugin_settings.get(plugin_name, {})
            # Instantiate the plugin with its settingr, if available.
            plugin = plugin_class(settings=this_plugin_settings)
        except Exception as exc:
            msg = f"Error initializing plugin '{plugin_class}': {exc!s}"
            raise ImproperlyConfigured(msg) from exc
        else:
            return plugin


# Instantiate the global plugin registry
registry = PluginRegistry()
