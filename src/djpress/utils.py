"""Utility functions that are used in the project."""

from collections.abc import Callable

from django.contrib.auth.models import User
from django.template.loader import TemplateDoesNotExist, select_template
from django.utils import timezone
from django.utils.module_loading import import_string

from djpress.conf import settings as djpress_settings


def get_markdown_renderer() -> Callable:
    """Get the configured markdown renderer function.

    Returns:
        callable: The markdown renderer function.
    """
    renderer_path = djpress_settings.MARKDOWN_RENDERER
    if not isinstance(renderer_path, str):  # pragma: no cover
        msg = f"Expected MARKDOWN_RENDERER to be a string, got {type(renderer_path).__name__}"
        raise TypeError(msg)

    try:
        return import_string(renderer_path)
    except ImportError as exc:
        from django.core.exceptions import ImproperlyConfigured

        msg = f"Could not import markdown renderer '{renderer_path}': {exc}"
        raise ImproperlyConfigured(msg) from exc


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

    if view_name == "tag_posts":
        template = f"djpress/{theme}/tag.html"

    if view_name == "author_posts":
        template = f"djpress/{theme}/author.html"

    if view_name == "single_post":
        template = f"djpress/{theme}/single.html"

    if view_name == "single_page":
        template = f"djpress/{theme}/page.html"

    if view_name == "search":
        template = f"djpress/{theme}/search.html"

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
        selected_template = getattr(select_template(templates), "template", None)
        template_name = getattr(selected_template, "name", None)
    except TemplateDoesNotExist as exc:
        msg = f"No template found for view '{view_name}'"
        raise TemplateDoesNotExist(msg) from exc

    return str(template_name)
