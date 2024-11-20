# Plugins

DJ Press includes a plugin system that allows you to extend its functionality. Plugins can modify content before and
after rendering, and future versions will include more hook points for customization.

## Creating a Plugin

To create a plugin, create a new Python package with the following structure:

```text
djpress_my_plugin/
    __init__.py
    plugin.py
```

In `plugin.py`, create a class called `Plugin` that inherits from `DJPressPlugin`:

```python
from djpress.plugins import DJPressPlugin

class Plugin(DJPressPlugin):
    name = "djpress_my_plugin"  # Required - recommended to be the same as the package name

    def setup(self, registry):
        # Register your hook callbacks
        registry.register_hook("pre_render_content", self.modify_content)
        registry.register_hook("post_render_content", self.modify_html)

    def modify_content(self, content: str) -> str:
        """Modify the markdown content before rendering."""
        # Create your code here...
        return content

    def modify_html(self, content: str) -> str:
        """Modify the HTML after rendering."""
        # Create your code here...
        return content
```

## Saving Plugin Data

Plugins can store a blob of JSON data in the database through the use of a JSONField on the PluginStorage model.

To retrieve the data, plugins can use: `data = self.get_data()`, and to save the data: `self.save_data(data)`.

## Available Hooks

Currently available hooks:

- `pre_render_content`: Called before markdown content is rendered to HTML. Passes the content to the plugin and
  expects to get content back.
- `post_render_content`: Called after markdown content is rendered to HTML. Passes the content to the plugin and
  expects to get content back.
- `post_save_post`: Called after saving a published post. Passes the published post to the plugin and ignores any
  returned values.

**Note** that you can also import the `Hooks` enum class, and reference the hook names specifically, e.g.
`from djpress.plugins import Hooks` and then you can refer to the above hooks as follows:

- `Hooks.PRE_RENDER_CONTENT`
- `Hooks.POST_RENDER_CONTENT`
- `Hooks.POST_SAVE_POST`

Each hook receives a value as its first argument and returns a value to be used by DJ Press. For example, the hooks
relating to rendering content expect to receive content back to continue processing. However, the `POST_SAVE_POST` hook
ignores any returned values since it has finished processing that step.

## Installing Plugins

- Install your plugin package:

```bash
pip install djpress-my-plugin
```

- Add the plugin to your DJ Press settings by adding the package name of your plugin to the `PLUGINS` key in `DJPRESS_SETTINGS`.
  If you use the recommended file structure for your plugin as described above, you only need the package name,
  i.e. this assumes your plugin code resides in a class called `Plugin` in a module called `plugins.py`

```python
DJPRESS_SETTINGS = {
    "PLUGINS": [
        "djpress_my_plugin"
    ],
}
```

- If you have a more complex plugin or you prefer a different style of packaging your plugin, you must use the full
  path to your plugin class. For example, if your package name is `djpress_my_plugin` and the module with your plugin
  class is `custom.py` and the plugin class is called `MyPlugin`, you'd need to use the following format:

```python
DJPRESS_SETTINGS = {
    "PLUGINS": [
        "djpress_my_plugin.custom.MyPlugin"
    ],
}
```

## Plugin Configuration

Plugins can receive configuration through the `PLUGIN_SETTINGS` dictionary. Access settings in your plugin using `self.config`.

For example, here is the `PLUGIN_SETTINGS` from the example plugin in this repository. **Note** that the dictionary key
is the `name` of the plugin and not the package name. It's recommended to keep the `name` of the plugin the same as the
package name, otherwise it will get confusing.

```python
DJPRESS_SETTINGS = {
    "PLUGINS": ["djpress_example_plugin"],  # this is the package name!
    "PLUGIN_SETTINGS": {
        "djpress_example_plugin": {  # this is the plugin name!
            "pre_text": "Hello, this text is configurable!",
            "post_text": "Goodbye, this text is configurable!",
        },
    },
}
```

In your plugin, you can access these settings using `self.config.get("pre_text")` or `self.config.get("post_text")`.

## Plugin Development Guidelines

1. You must define a unique `name` for your plugin and strongly recommend this is the same as the package name.
2. Handle errors gracefully - don't let your plugin break the site.
3. Use type hints for better code maintainability.
4. Include tests for your plugin's functionality.
5. Document any settings your plugin uses.

## System Checks

DJ Press includes system checks that will warn about:

- Unknown hooks (might indicate deprecated hooks or version mismatches)

Run Django's check framework to see any warnings:

```bash
python manage.py check
```
