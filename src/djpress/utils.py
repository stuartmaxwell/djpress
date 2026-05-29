"""Utility functions that are used in the project."""

from collections.abc import Callable

from django.contrib.auth.models import AbstractBaseUser
from django.core.exceptions import ImproperlyConfigured
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
        msg = f"Could not import markdown renderer '{renderer_path}': {exc}"
        raise ImproperlyConfigured(msg) from exc


def get_author_display_name(user: AbstractBaseUser) -> str:
    """Return the author display name.

    Tries to display the first name and last name if available, otherwise falls back to
    the username.

    Order of preference:

    1. If the User model implements a `get_full_name` method, use it
    2. If the User model implements a `first_name` field and a `last_name` field, use them
    3. Fall back to the `get_username()` method that is available on the `AbstractBaseUser` model

    Args:
        user: The user.

    Returns:
        str: The author display name.
    """
    get_full_name = getattr(user, "get_full_name", None)
    if get_full_name and callable(get_full_name):
        name = get_full_name().strip()
        if name:
            return name

    first_name = getattr(user, "first_name", None)
    last_name = getattr(user, "last_name", None)
    if first_name and last_name:
        return f"{first_name} {last_name}".strip()
    if first_name:
        return first_name
    if last_name:
        return last_name

    return user.get_username()


def validate_date_parts(year: str | None, month: str | None, day: str | None) -> dict[str, int]:
    """Validate the date parts.

    Parts are passed as strings and converted to integers. Then a datetimeobject is attempted to be created.

    A year must be provided if a month is provided.
    A month must be provided if a day is provided.

    Args:
        year (str | None): The year.
        month (str | None): The month.
        day (str | None): The day.

    Returns:
        dict[str, int]: The validated date parts - the dates are converted to integers.

    Raises:
        ValueError: If the date is invalid.
    """
    error_msg = "Invalid date"

    # Check that the correct parts have been provided
    if month and not year:
        raise ValueError(error_msg)
    if day and not month:
        raise ValueError(error_msg)

    # Test that the provided parts can form a valid date
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
        raise ValueError(error_msg) from exc

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
