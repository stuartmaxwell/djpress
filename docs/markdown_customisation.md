# Customising Markdown Rendering

DJ Press uses Markdown for content rendering, providing a familiar and flexible syntax for blog authors. This document
explains how to customise the Markdown rendering in your blog.

## Basic Configuration

DJ Press uses the Python-Markdown library for rendering Markdown content. You can customise the rendering by
configuring the following settings in your `settings.py` file:

```python
DJPRESS_SETTINGS = {
    # Markdown settings
    "MARKDOWN_EXTENSIONS": ["extra", "codehilite", "toc"],
    "MARKDOWN_EXTENSION_CONFIGS": {
        "codehilite": {
            "css_class": "highlight",
            "linenums": True,
        },
        "toc": {
            "permalink": True,
        },
    },
}
```

### Available Settings

| Setting                      | Type | Default                                        | Description                                    |
|------------------------------|------|------------------------------------------------|------------------------------------------------|
| `MARKDOWN_EXTENSIONS`        | list | `[]`                                           | List of Python-Markdown extensions to enable.  |
| `MARKDOWN_EXTENSION_CONFIGS` | dict | `{}`                                           | Configuration options for markdown extensions. |
| `MARKDOWN_RENDERER`          | str  | `"djpress.markdown_renderer.default_renderer"` | Path to markdown renderer function.            |

## Recommended Extensions

Here are some popular Python-Markdown extensions you may want to consider:

1. **extra** - Combines several extensions that emulate PHP Markdown Extra
2. **codehilite** - Syntax highlighting for code blocks
3. **toc** - Table of contents generation
4. **admonition** - For adding note/warning blocks
5. **nl2br** - Converts newlines to HTML line breaks
6. **smarty** - For smart typography (quotes, dashes, etc.)
7. **wikilinks** - For easier internal linking with [[WikiStyle]] syntax

Example configuration with multiple extensions:

```python
DJPRESS_SETTINGS = {
    "MARKDOWN_EXTENSIONS": [
        "extra",
        "codehilite",
        "toc",
        "admonition",
        "nl2br",
        "smarty",
    ],
    "MARKDOWN_EXTENSION_CONFIGS": {
        "codehilite": {
            "css_class": "highlight",
            "linenums": False,
            "guess_lang": False,
        },
        "toc": {
            "permalink": True,
            "baselevel": 2,
        },
    },
}
```

## Custom Markdown Renderer

For more advanced customisation, you can create a custom Markdown renderer function. This allows you to:

1. Apply pre-processing to the Markdown before rendering
2. Use a different Markdown library or renderer
3. Apply post-processing to the rendered HTML
4. Add custom extensions or filters

### Example: Creating a Custom Renderer

This is a basic example of creating your own markdown renderer that uses the Mistune library.

```python
# myapp/markdown_renderer.py
import mistune

def mistune_renderer(markdown_text: str) -> str:
    """Render markdown text using Mistune.

    We use our custom rendered with the same defaults as the Mistune renderer.

    Args:
        markdown_text (str): The markdown text.

    Returns:
        str: The rendered markdown text.
    """
    markdown = mistune.create_markdown(
        escape=False,
        plugins=[
            "strikethrough",
            "table",
            "footnotes",
        ],
    )
    return markdown(markdown_text)
```

Then configure DJ Press to use your custom renderer in `settings.py`:

```python
DJPRESS_SETTINGS = {
    "MARKDOWN_RENDERER": "myapp.markdown_renderer.mistune_renderer",
}
```

## Further Resources

- [Python-Markdown Documentation](https://python-markdown.github.io/)
- [Python-Markdown Extensions](https://python-markdown.github.io/extensions/)
- [Bleach Documentation](https://bleach.readthedocs.io/) (for HTML sanitisation)
- [Pygments Documentation](https://pygments.org/docs/) (for syntax highlighting)

## Related Topics

- [Configuration](configuration.md) - More settings for customising DJ Press
- [Themes](themes.md) - How to style and structure your blog
