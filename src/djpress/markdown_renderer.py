"""Default Markdown renderer for Djpress."""

import markdown

from djpress.conf import settings as djpress_settings


def default_renderer(markdown_text: str) -> str:
    """Return the Markdown text as HTML."""
    md = markdown.Markdown(
        extensions=djpress_settings.MARKDOWN_EXTENSIONS,
        extension_configs=djpress_settings.MARKDOWN_EXTENSION_CONFIGS,
        output_format="html",
    )
    html = md.convert(markdown_text)
    md.reset()

    return html
