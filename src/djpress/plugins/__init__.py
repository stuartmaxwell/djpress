"""Plugins module for djpress."""

from djpress.plugins.base_plugin import DJPressPlugin
from djpress.plugins.hook_registry import Hooks
from djpress.plugins.plugin_registry import PluginRegistry, registry

__all__ = ["DJPressPlugin", "Hooks", "PluginRegistry", "registry"]
