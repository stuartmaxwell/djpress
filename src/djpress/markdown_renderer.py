"""Default Markdown renderer for Djpress."""

import markdown

from djpress.conf import settings as djpress_settings


def default_renderer(markdown_text: str) -> str:
    """Return the Markdown text as HTML."""
    markdown_extensions = djpress_settings.MARKDOWN_EXTENSIONS
    if not isinstance(markdown_extensions, list) and markdown_extensions is not None:
        msg = f"Expected MARKDOWN_EXTENSIONS to be a list, got {type(markdown_extensions).__name__}"
        raise TypeError(msg)
    markdown_extension_configs = djpress_settings.MARKDOWN_EXTENSION_CONFIGS
    if not isinstance(markdown_extension_configs, dict) and markdown_extension_configs is not None:
        msg = f"Expected MARKDOWN_EXTENSION_CONFIGS to be a dict, got {type(markdown_extension_configs).__name__}"
        raise TypeError(msg)

    md = markdown.Markdown(
        extensions=markdown_extensions,
        extension_configs=markdown_extension_configs,
        output_format="html",
    )
    html = md.convert(markdown_text)
    md.reset()

    return html
