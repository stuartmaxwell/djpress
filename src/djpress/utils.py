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


def get_templates(view_name: str) -> list[str]:
    """Get the template names for a view.

    Args:
        view_name (str): The view name.

    Returns:
        list[str]: The list of template names.
    """
    theme = djpress_settings.THEME

    template = ""

    if view_name == "index":
        template = f"djpress/{theme}/home.html"

    if view_name == "archive_posts":
        template = f"djpress/{theme}/archives.html"

    if view_name == "category_posts":
        template = f"djpress/{theme}/category.html"

    if view_name == "author_posts":
        template = f"djpress/{theme}/author.html"

    if view_name == "single_post":
        template = f"djpress/{theme}/single.html"

    if view_name == "single_page":
        template = f"djpress/{theme}/single.html"

    default_template = f"djpress/{theme}/index.html"

    return [template, default_template] if template else [default_template]


def get_template_name(view_name: str) -> str:
    """Return the first template that exists.

    Args:
        view_name (str): The view name

    Returns:
        str: The template name.
    """
    templates = get_templates(view_name)

    try:
        template = str(select_template(templates).template.name)
    except TemplateDoesNotExist as exc:
        msg = "No template found"
        raise TemplateDoesNotExist(msg) from exc

    return template
