"""An example DJ Press plugin."""

import logging

from djpress.plugins import DJPressPlugin, Hooks, PluginRegistry

logger = logging.getLogger(__name__)


class Plugin(DJPressPlugin):
    """An example DJ Press plugin."""

    name = "djpress_example_plugin"

    def __init__(self) -> None:
        """Initisalize the plugin."""
        super().__init__()

    def setup(self, registry: PluginRegistry) -> None:
        """Set up the plugin.

        Args:
            registry (Hooks): The plugin registry.
        """
        registry.register_hook(Hooks.PRE_RENDER_CONTENT, self.add_greeting)
        registry.register_hook(Hooks.POST_RENDER_CONTENT, self.add_goodbye)

    def add_greeting(self, content: str) -> str:
        """Add a greeting to the content.

        This is a pre-render hook, so the content is still in Markdown format.

        Args:
            content (str): The content to modify.

        Returns:
            str: The modified content.
        """
        return f"Hello, world! This was added by `djpress_example_plugin`!\n\n---\n\n{content}"

    def add_goodbye(self, content: str) -> str:
        """Add a goodbye message to the content.

        This is a post-render hook, so the content has already been rendered from Markdown to HTML.

        Args:
            content (str): The content to modify.

        Returns:
            str: The modified content.
        """
        return f"{content}<hr><p>Goodbye, world! This was added by <code>djpress_example_plugin</code>!</p>"
