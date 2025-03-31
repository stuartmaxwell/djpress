"""An example DJ Press plugin."""

from djpress.plugins import DJPressPlugin, PluginRegistry


class Plugin(DJPressPlugin):
    """An example DJ Press plugin."""

    name = "djpress_example_plugin"

    def setup(self, registry: PluginRegistry) -> None:
        """Set up the plugin.

        Args:
            registry (Hooks): The plugin registry.
        """
        registry.register_hook("pre_render_content", self.add_greeting)
        registry.register_hook("post_render_content", self.add_goodbye)
        registry.register_hook("admin_post_buttons", self.word_count_button)

    def add_greeting(self, content: str) -> str:
        """Add a greeting to the content.

        This is a pre-render hook, so the content is still in Markdown format.

        Args:
            content (str): The content to modify.

        Returns:
            str: The modified content.
        """
        greeting = self.config.get("pre_text", "Hello!")
        return f"{greeting} This was added by `djpress_example_plugin`!\n\n---\n\n{content}"

    def add_goodbye(self, content: str) -> str:
        """Add a goodbye message to the content.

        This is a post-render hook, so the content has already been rendered from Markdown to HTML.

        Args:
            content (str): The content to modify.

        Returns:
            str: The modified content.
        """
        goodbye = self.config.get("pre_text", "Goodbye!")
        return f"{content}<hr><p>{goodbye} This was added by <code>djpress_example_plugin</code>!</p>"

    # Register a button in the admin post edit screen. The name of the button must match the
    # name of the function that handles the action.
    word_count_button = {
        "name": "count_words",
        "plugin_name": "djpress_example_plugin",
        "label": "Count Words",
        "style": "info",
    }

    def count_words(self, post_id: int) -> str:
        """Count the words in a post."""
        from djpress.models import Post

        post = Post.objects.get(pk=post_id)

        word_count = len(post.content.split())

        return f"Word count: {word_count} words"
