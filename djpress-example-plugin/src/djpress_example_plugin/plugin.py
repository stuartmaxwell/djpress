"""An example DJ Press plugin."""

from djpress.plugins import DJPressPlugin, PluginRegistry


class Plugin(DJPressPlugin):
    """An example DJ Press plugin."""

    name = "djpress_example_plugin"

    def setup(self, registry: PluginRegistry) -> None:
        """Set up the plugin.

        Args:
            registry (PluginRegistry): The plugin registry.
        """
        registry.register_hook("pre_render_content", self.add_greeting)
        registry.register_hook("post_render_content", self.add_goodbye)
        registry.register_hook("dj_header", self.add_header_content)
        registry.register_hook("dj_footer", self.add_footer_content)

    def add_greeting(self, content: str) -> str:
        """Add a greeting to the content.

        This is a pre-render hook, so the content is still in Markdown format.

        Args:
            content (str): The content to modify.

        Returns:
            str: The modified content.
        """
        return f"{self.config.get('pre_text')} This was added by `djpress_example_plugin`!\n\n---\n\n{content}"

    def add_goodbye(self, content: str) -> str:
        """Add a goodbye message to the content.

        This is a post-render hook, so the content has already been rendered from Markdown to HTML.

        Args:
            content (str): The content to modify.

        Returns:
            str: The modified content.
        """
        return (
            f"{content}<hr><p>{self.config.get('pre_text')} This was added by <code>djpress_example_plugin</code>!</p>"
        )

    def add_header_content(self, _: str = "") -> str:
        """Add content to the HTML head section.

        This hook allows the plugin to inject content into the <head> section of HTML templates.

        Args:
            content (str): The existing header content.

        Returns:
            str: The modified header content.
        """
        return """
<!-- Example Plugin Header Content -->
<style>
    .example-plugin-footer { color: #007cba; font-weight: bold; background-color: #f0f0f0; padding: 10px; }
</style>"""

    def add_footer_content(self, _: str = "") -> str:
        """Add content to the HTML footer section.

        This hook allows the plugin to inject content near the end of HTML documents.

        Args:
            content (str): The existing footer content.

        Returns:
            str: The modified footer content.
        """
        return """
<div class="example-plugin-footer">
    <p>This content was added by <code>djpress_example_plugin</code>.</p>
</div>"""
