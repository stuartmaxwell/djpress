"""Utility functions that are used in the project."""

import markdown
from django.conf import settings
from django.contrib.auth.models import User

md = markdown.Markdown(extensions=settings.MARKDOWN_EXTENSIONS, output_format="html")


def render_markdown(markdown_text: str) -> str:
    """Return the Markdown text as HTML."""
    html = md.convert(markdown_text)
    md.reset()

    return html


def get_author_display_name(user: User) -> str:
    """Return the author display name.

    Tries to display the first name and last name if available, otherwise falls back to
    the username.

    Args:
        user: The user.

    Returns:
        str: The author display name.
    """
    if user.first_name and user.last_name:
        return f"{user.first_name} {user.last_name}"

    if user.first_name:
        return user.first_name

    return user.username
