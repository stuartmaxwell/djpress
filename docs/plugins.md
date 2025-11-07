# Plugins

DJ Press includes a plugin system that allows you to extend its functionality. Plugins can modify content before and
after rendering, send notifications when content is published, and more. The plugin system is designed to be easy to
use while still being powerful enough for complex extensions.

## Plugin Lifecycle

The DJ Press plugin system follows this lifecycle:

1. **Discovery** - Plugins are loaded from the `PLUGINS` setting during application startup
2. **Registration** - Plugins register callbacks for specific hooks
3. **Execution** - Callbacks are executed when hooks are triggered during normal application operation
4. **Cleanup** - When Django shuts down, plugins can perform cleanup (if needed)

## Creating a Plugin

To create a plugin, create a new Python package with the following structure:

```text
djpress_my_plugin/
    __init__.py
    plugin.py
    tests/
        __init__.py
        test_plugin.py
```

In `plugin.py`, create a class called `Plugin` that inherits from `DJPressPlugin`:

```python
from djpress.plugins import DJPressPlugin
from djpress.plugin.hook_registry import PRE_RENDER_CONTENT, POST_RENDER_CONTENT, POST_SAVE_POST, SEARCH_CONTENT

class Plugin(DJPressPlugin):
    name = "djpress_my_plugin"  # Required - use same name as package
    hooks = [
        (PRE_RENDER_CONTENT, "modify_content"),
        (POST_RENDER_CONTENT, "modify_html"),
        (POST_SAVE_POST, "notify_on_publish"),
        (SEARCH_CONTENT, "custom_search"),
    ]


    def modify_content(self, content: str) -> str:
        """Modify the markdown content before rendering.

        This callback implements the PreRenderHook signature.

        Args:
            content: The raw markdown content

        Returns:
            Modified markdown content
        """
        try:
            # Always wrap plugin code in try/except to prevent site breakage
            if not content or not isinstance(content, str):
                return content

            # Example: Add a header to all content
            prefix = self.config.get("prefix_text", "")
            if prefix:
                content = f"{prefix}\n\n{content}"

            return content
        except Exception as e:
            # Log the error but don't break the site
            import logging
            logging.error(f"Error in modify_content: {e}")
            return content

    def modify_html(self, html_content: str) -> str:
        """Modify the HTML after markdown rendering.

        Args:
            html_content: The rendered HTML content

        Returns:
            Modified HTML content
        """
        try:
            # Example: Add a footer to all content
            suffix = self.config.get("suffix_text", "")
            if suffix and html_content:
                html_content = f"{html_content}<div class='plugin-footer'>{suffix}</div>"
            return html_content
        except Exception as e:
            import logging
            logging.error(f"Error in modify_html: {e}")
            return html_content

    def notify_on_publish(self, post):
        """Send notification when a post is published.

        Args:
            post: The Post object that was published

        Returns:
            None (return value is ignored for this hook)
        """
        try:
            # Example: Track published posts in plugin storage
            data = self.get_data() or {"published_posts": []}

            # Add the post ID to our tracking list if not already there
            if post.id not in data.get("published_posts", []):
                data.setdefault("published_posts", []).append(post.id)
                self.save_data(data)

            # Example: Could send an email, ping a webhook, etc.
            if self.config.get("send_notifications"):
                self._send_notification(post)
        except Exception as e:
            import logging
            logging.error(f"Error in notify_on_publish: {e}")

    def _send_notification(self, post):
        """Private helper method to send notifications."""
        # Implementation would depend on notification method
        pass

    def custom_search(self, query: str):
        """Provide custom search functionality.

        This callback implements the SearchProvider signature.

        Args:
            query: The search query string

        Returns:
            QuerySet of Post objects matching the search
        """
        try:
            from djpress.models import Post

            # Example: Custom search using Django's full-text search
            # This is just an example - implement your own logic
            if not query:
                return Post.objects.none()

            # You could use PostgreSQL full-text search, Elasticsearch, etc.
            # For this example, we'll do a simple case-insensitive search
            return Post.objects.filter(
                title__icontains=query
            ) | Post.objects.filter(
                content__icontains=query
            )
        except Exception as e:
            import logging
            logging.error(f"Error in custom_search: {e}")
            # Return None to fall back to default search
            return None
```

## Saving Plugin Data

Plugins can store data in the database through the `PluginStorage` model. This is useful for maintaining state between
requests or for caching data.

```python
# Get the current data (returns None if no data exists)
data = self.get_data()

# Initialise if needed
if data is None:
    data = {"counter": 0, "settings": {}}

# Update the data
data["counter"] += 1
data["settings"]["last_updated"] = str(timezone.now())

# Save the data back to the database
self.save_data(data)
```

The data must be JSON-serialisable (dictionaries, lists, strings, numbers, booleans, or None).

## Available Hooks

DJ Press provides these hooks for plugins:

| Hook Name             | Description                                           | Arguments                 | Expected Return                    |
|-----------------------|-------------------------------------------------------|---------------------------|------------------------------------|
| `PRE_RENDER_CONTENT`  | Called before markdown content is rendered to HTML    | `content: str` (markdown) | Modified markdown content          |
| `POST_RENDER_CONTENT` | Called after markdown content is rendered to HTML     | `content: str` (HTML)     | Modified HTML content              |
| `POST_SAVE_POST`      | Called after saving a published post                  | `post: Post` (object)     | None (return ignored)              |
| `SEARCH_CONTENT`      | Override default search with custom implementation    | `query: str`              | QuerySet of Post objects, or None  |
| `DJ_HEADER`           | Used to insert HTML into the template's `<head>` tag. | None                      | HTML content (`str`)               |
| `DJ_FOOTER`           | Called after saving a published post                  | `post: Post` (object)     | None (return ignored)              |

Hooks are imported from the `hook_registry` module, and then assigned to a list called `hooks` in the `Plugin` class.
The hook is added to the list as a tuple with the first element being the hook, and the second element being the string
name of the callable.

```python
from djpress.plugin.hook_registry import PRE_RENDER_CONTENT

# Define a hooks list of tuples:
    hooks = [(PRE_RENDER_CONTENT, "modify_content")]
```

## Installing Plugins

To install a plugin, follow these steps:

1. Install the plugin package:

```bash
pip install djpress-my-plugin
```

1. Add the plugin to your settings:

```python
DJPRESS_SETTINGS = {
    "PLUGINS": [
        "djpress_my_plugin"  # Package name
    ],
}
```

1. Run migrations and restart your server:

```bash
python manage.py migrate
```

If your plugin is structured differently, specify the full path:

```python
DJPRESS_SETTINGS = {
    "PLUGINS": [
        "djpress_my_plugin.custom.MyPlugin"  # Full path to class
    ],
}
```

## Plugin Configuration

Configure plugins using the `PLUGIN_SETTINGS` dictionary:

```python
DJPRESS_SETTINGS = {
    "PLUGINS": ["djpress_example_plugin"],
    "PLUGIN_SETTINGS": {
        "djpress_example_plugin": {  # Must match plugin's 'name'
            "prefix_text": "### Featured Content",
            "suffix_text": "<em>Thanks for reading!</em>",
            "send_notifications": True,
            "notification_email": "admin@example.com",
        },
    },
}
```

Access settings in your plugin using `self.config`:

```python
# Get with default value if setting doesn't exist
prefix = self.config.get("prefix_text", "Default prefix")

# Check if a setting exists
if "send_notifications" in self.config:
    # Do something
```

## Error Handling

Proper error handling is essential for plugins. Always wrap your code in try/except blocks:

```python
def my_hook_handler(self, content):
    try:
        # Your code here
        return modified_content
    except Exception as e:
        import logging
        logging.error(f"Plugin error in my_hook_handler: {e}")
        # Return original content to avoid breaking the site
        return content
```

## Plugin Development Guidelines

1. **Unique Name**: Define a unique `name` property that matches your package name.
2. **Error Handling**: Always use try/except to prevent crashing the site.
3. **Type Hints**: Use type hints for better code maintainability.
4. **Documentation**: Document your plugin's purpose, hooks, and configuration options.
5. **Testing**: Include comprehensive tests for your plugin's functionality.
6. **Performance**: Be mindful of performance in hooks that run frequently.
7. **Security**: Validate and sanitise any user-provided data.

## System Checks

DJ Press includes system checks that will warn about:

- Unknown hooks (might indicate deprecated hooks or version mismatches)
- Plugins that fail to load or initialise properly

Run Django's check framework to see any warnings:

```bash
python manage.py check
```

## Complete Example Plugin

Check out the [example plugin](https://github.com/stuartmaxwell/djpress/tree/main/djpress-example-plugin)
included with DJ Press for a working reference implementation.
