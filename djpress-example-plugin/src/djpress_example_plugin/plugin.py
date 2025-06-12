"""An example DJ Press plugin."""

from typing import TYPE_CHECKING

from djpress.plugins import DJPressPlugin
from djpress.plugins.hook_registry import (
    DJ_FOOTER,
    DJ_HEADER,
    POST_RENDER_CONTENT,
    POST_SAVE_POST,
    PRE_RENDER_CONTENT,
)

if TYPE_CHECKING:
    from djpress.models import Post


class Plugin(DJPressPlugin):
    """An example DJ Press plugin.

    Attributes:
        hooks: List of (hook, method_name) pairs for automatic registration.
    """

    name = "djpress_example_plugin"
    hooks = [
        (PRE_RENDER_CONTENT, "add_greeting"),
        (POST_RENDER_CONTENT, "add_goodbye"),
        (DJ_HEADER, "add_header_content"),
        (DJ_FOOTER, "add_footer_content"),
        (POST_SAVE_POST, "log_post_data"),
    ]

    def add_greeting(self, content: str) -> str:
        """Add a greeting to the content.

        This is a pre-render hook, so the content is still in Markdown format.

        `greet_text` can be set in the plugin settings, or defaults to "Hello!".

        Args:
            content: The content to modify.

        Returns:
            The modified content.
        """
        greet_text = self.settings.get("greet_text", "Hello!")
        return f"{greet_text} This was added by `add_greeting` in `djpress_example_plugin`!\n\n---\n\n{content}"

    def add_goodbye(self, content: str) -> str:
        """Add a goodbye message to the content.

        This is a post-render hook, so the content has already been rendered from Markdown to HTML.

        `bye_text` can be set in the plugin settings, or defaults to "Goodbye!".

        Args:
            content: The content to modify.

        Returns:
            The modified content.
        """
        bye_text = self.settings.get("bye_text", "Goodbye!")
        return (
            f"{content}<hr><p>{bye_text} Added by <code>add_goodbye</code> in <code>djpress_example_plugin</code>!</p>"
        )

    def add_header_content(self) -> str:
        """Add content to the HTML head section.

        This hook allows the plugin to inject content into the <head> section of HTML templates.

        Returns:
            The modified header content.
        """
        return """
<!-- Example Plugin Header Content -->
<style>
    .example-plugin-footer { color: #007cba; font-weight: bold; background-color: #f0f0f0; padding: 10px; }
</style>"""

    def add_footer_content(self) -> str:
        """Add content to the HTML footer section.

        This hook allows the plugin to inject content near the end of HTML documents.

        Returns:
            The modified footer content.
        """
        return """
<div class="example-plugin-footer">
    <p>This content was added by <code>djpress_example_plugin</code>.</p>
</div>"""

    def log_post_data(self, post: "Post") -> "Post":
        """Log the post data after it has been saved.

        This is a post-save hook that allows the plugin to perform actions after a Post object is saved.

        Args:
            post: The Post object that was saved.
        """
        # Here we just log the post title and ID as an example
        print(f"Post saved: {post.title} (ID: {post.pk})")  # noqa: T201

        return post
