"""PluginStorage model for storing plugin data in the database."""

from django.db import models


class PluginStorageManager(models.Manager):
    """Manager for the PluginStorage model."""

    def get_data(self, plugin_name: str) -> dict:
        """Get plugin data.

        Retrieve the plugin data from the database. If the plugin data does not exist, return an empty dictionary.

        Args:
            plugin_name (str): The name of the plugin.

        Returns:
            dict: The plugin data.
        """
        try:
            data = self.get(plugin_name=plugin_name)
        except self.model.DoesNotExist:
            return {}
        else:
            return data.plugin_data or {}

    def save_data(self, plugin_name: str, data: dict) -> None:
        """Save plugin data.

        Save or update the plugin data in the database. If no storage exists for this plugin, it will be created.

        Args:
            plugin_name (str): The name of the plugin.
            data (dict): The plugin data.

        Returns:
            None
        """
        storage, created = self.update_or_create(
            plugin_name=plugin_name,
            defaults={"plugin_data": data},
        )


class PluginStorage(models.Model):
    """Model for storing plugin data in the database."""

    # Manager
    objects: PluginStorageManager = PluginStorageManager()

    plugin_name = models.CharField(max_length=100, unique=True)
    plugin_data = models.JSONField(default=dict)

    class Meta:
        """Meta options for the PluginStorage model."""

        verbose_name = "plugin storage"
        verbose_name_plural = "plugin storage"

    def __str__(self) -> str:
        """Return the string representation of the plugin item."""
        return self.plugin_name
