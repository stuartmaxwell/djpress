"""Plugin system for DJ Press."""

import logging

from djpress.conf import settings as djpress_settings
from djpress.models import PluginStorage
from djpress.plugins.hook_registry import _Hook

logger = logging.getLogger(__name__)


class DJPressPlugin:
    """Base class for DJ Press plugins.

    You must provide a `name` attribute and define `hooks` as a list of tuples containing the hook and the method name
    to call.
    """

    name: str
    hooks: list[tuple[_Hook, str]] = []

    def __init__(self) -> None:
        """Initialize the plugin."""

    @property
    def settings(self) -> dict:
        """Dynamically fetch plugin configuration settings at runtime."""
        try:
            plugin_settings = getattr(djpress_settings, "PLUGIN_SETTINGS", {})
        except (TypeError, AttributeError):
            plugin_settings = {}

        if not isinstance(plugin_settings, dict):
            return {}
        return plugin_settings.get(self.name, {})

    @property
    def config(self) -> dict:
        """Alias for self.settings to preserve compatibility with documentation."""
        return self.settings

    def get_data(self) -> dict:
        """Get this plugin's stored data.

        Returns:
            dict: The plugin's stored data, or empty dict if none exists.
        """
        return PluginStorage.objects.get_data(self.name)

    def save_data(self, data: dict) -> None:
        """Save this plugin's data.

        Args:
            data: The data to store for this plugin.
        """
        PluginStorage.objects.save_data(self.name, data)
