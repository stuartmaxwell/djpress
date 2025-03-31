"""An example DJ Press plugin."""

import random
from typing import Any

from djpress.plugins import DJPressPlugin, Hooks, PluginRegistry


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
        registry.register_hook(Hooks.ADMIN_POST_BUTTONS, self.register_admin_buttons)
        registry.register_hook(Hooks.ADMIN_POST_BUTTONS, self.handle_admin_button_action)

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

    def register_admin_buttons(self, buttons: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Register admin buttons for the plugin.

        This hook registers button definitions that will be displayed in the admin.

        Args:
            buttons (List[Dict[str, Any]]): Current list of buttons.

        Returns:
            List[Dict[str, Any]]: Updated list of buttons with our additions.
        """
        if not isinstance(buttons, list):
            buttons = []

        # Add a button to generate a random tag
        buttons.append(
            {
                "name": "add_random_tag",
                "plugin_name": self.name,
                "label": "Add Random Tag",
                "style": "success",
            },
        )

        # Add a button to count words
        buttons.append(
            {
                "name": "count_words",
                "plugin_name": self.name,
                "label": "Count Words",
                "style": "info",
            },
        )

        return buttons

    def handle_admin_button_action(self, data: dict[str, Any]) -> dict[str, Any]:
        """Handle admin button actions.

        This hook processes button clicks from the admin interface.

        Args:
            data (Dict[str, Any]): Data containing post and plugin info.

        Returns:
            Dict[str, Any]: Result data to return to the admin.
        """
        # Check if this is a button action call
        if not isinstance(data, dict) or "post" not in data or "plugin_name" not in data:
            return data

        # Check if this is for our plugin
        if data["plugin_name"] != self.name:
            return data

        post = data["post"]

        # Add a random tag action
        if "add_random_tag" in data.get("action", ""):
            random_tags = ["example", "plugin", "demo", "testing", "random", "sample"]
            # This is just a demo, not security-critical
            random_tag = random.choice(random_tags)  # noqa: S311

            # Check if tag exists and add it
            from djpress.models import Tag

            tag, _ = Tag.objects.get_or_create(title=random_tag, slug=random_tag)
            post.tags.add(tag)
            post.save()

            return {
                "success": True,
                "message": f"Added random tag: {random_tag}",
            }

        # Count words action
        if "count_words" in data.get("action", ""):
            word_count = len(post.content.split())

            return {
                "success": True,
                "message": f"Word count: {word_count} words",
                "word_count": word_count,
            }

        return data
