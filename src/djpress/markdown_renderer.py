"""Default Markdown renderer for Djpress."""

import markdown

from djpress.conf import settings as djpress_settings


def default_renderer(markdown_text: str) -> str:
    """Return the Markdown text as HTML."""
    markdown_extensions = djpress_settings.MARKDOWN_EXTENSIONS
    if not isinstance(markdown_extensions, list):  # pragma: no cover
        msg = f"Expected list for MARKDOWN_EXTENSIONS, got {type(markdown_extensions).__name__}"
        raise TypeError(msg)

    markdown_extension_configs = djpress_settings.MARKDOWN_EXTENSION_CONFIGS
    if not isinstance(markdown_extension_configs, dict):  # pragma: no cover
        msg = f"Expected dict for MARKDOWN_EXTENSION_CONFIGS, got {type(markdown_extension_configs).__name__}"
        raise TypeError(msg)

    md = markdown.Markdown(
        extensions=markdown_extensions,
        extension_configs=markdown_extension_configs,
        output_format="html",
    )
    html = md.convert(markdown_text)
    md.reset()

    return html
