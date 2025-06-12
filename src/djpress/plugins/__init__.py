"""Plugins module for djpress."""

from djpress.plugins import hook_registry
from djpress.plugins.base_plugin import DJPressPlugin
from djpress.plugins.plugin_registry import registry

__all__ = [
    "DJPressPlugin",
    "hook_registry",
    "registry",
]
