"""Utility functions that are used in the project."""

import markdown
from django.contrib.auth.models import User
from django.template.loader import TemplateDoesNotExist, select_template
from django.utils import timezone

from djpress.conf import settings as djpress_settings


def render_markdown(markdown_text: str) -> str:
    """Return the Markdown text as HTML."""
    md = markdown.Markdown(
        extensions=djpress_settings.MARKDOWN_EXTENSIONS,
        extension_configs=djpress_settings.MARKDOWN_EXTENSION_CONFIGS,
        output_format="html",
    )
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


def validate_date_parts(year: str | None, month: str | None, day: str | None) -> dict:
    """Validate the date parts.

    Args:
        year (str | None): The year.
        month (str | None): The month.
        day (str | None): The day.

    Returns:
        dict: The validated date parts.

    Raises:
        ValueError: If the date is invalid.
    """
    result = {}

    try:
        if year:
            result["year"] = int(year)
        if month:
            result["month"] = int(month)
        if day:
            result["day"] = int(day)

        # If we have all parts, try to create a date
        if "year" in result and "month" in result and "day" in result:
            timezone.make_aware(timezone.datetime(result["year"], result["month"], result["day"]))
        elif "year" in result and "month" in result:
            # Validate just year and month
            timezone.make_aware(timezone.datetime(result["year"], result["month"], 1))
        elif "year" in result:
            # Validate just the year
            timezone.make_aware(timezone.datetime(result["year"], 1, 1))

    except ValueError as exc:
        msg = "Invalid date"
        raise ValueError(msg) from exc

    return result


def get_template_name(templates: list[str]) -> str:
    """Return the first template that exists.

    Args:
        templates (list[str]): The list of template names.

    Returns:
        str: The template name.
    """
    try:
        template = str(select_template(templates).template.name)
    except TemplateDoesNotExist as exc:
        msg = "No template found"
        raise TemplateDoesNotExist(msg) from exc

    return template
