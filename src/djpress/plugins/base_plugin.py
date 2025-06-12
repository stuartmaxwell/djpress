"""Plugin system for DJ Press."""

import logging

from djpress.plugins.hook_registry import _Hook

logger = logging.getLogger(__name__)


class DJPressPlugin:
    """Base class for DJ Press plugins.

    You must provide a `name` attribute and define `hooks` as a list of tuples containing the hook and the method name
    to call.
    """

    name: str
    hooks: list[tuple[_Hook, str]] = []

    def __init__(self, settings: dict) -> None:
        """Initialize the plugin with a configuration dictionary.

        If there are no settings, then an empty dict will be passed.

        Args:
            settings: A dictionary containing the settings for the plugin.
        """
        self.settings = settings

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
