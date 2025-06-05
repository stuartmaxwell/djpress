"""Plugin system for DJ Press."""

import logging

from djpress.plugins.plugin_registry import PluginRegistry

logger = logging.getLogger(__name__)


class DJPressPlugin:
    """Base class for DJ Press plugins."""

    name: str

    def __init__(self, config: dict | None = None) -> None:
        """Initialize the plugin."""
        if not hasattr(self, "name") or not self.name:
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
