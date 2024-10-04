"""Utility functions that are used in the project."""

import re
from typing import NamedTuple

import markdown
from django.contrib.auth.models import User
from django.template.loader import TemplateDoesNotExist, select_template
from django.utils import timezone

from djpress.conf import settings as djpress_settings
from djpress.exceptions import SlugNotFoundError


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


def validate_date(year: str, month: str, day: str) -> None:
    """Test the date values.

    Convert the date values to integers and test if they are valid dates.

    The regex that gets the date values checks for the following:
    - year: four digits
    - month: two digits
    - day: two digits

    Args:
        year (str): The year.
        month (str | None): The month.
        day (str | None): The day.

    Raises:
        ValueError: If the date is invalid.

    Returns:
        None
    """
    int_year: int = int(year)
    int_month: int | None = int(month) if month else None
    int_day: int | None = int(day) if day else None

    if int_month == 0 or int_day == 0:
        msg = "Invalid date"
        raise ValueError(msg)

    try:
        if int_month and int_day:
            timezone.make_aware(timezone.datetime(int_year, int_month, int_day))

        elif int_month:
            timezone.make_aware(timezone.datetime(int_year, int_month, 1))

        else:
            timezone.make_aware(timezone.datetime(int_year, 1, 1))

    except ValueError as exc:
        msg = "Invalid date"
        raise ValueError(msg) from exc


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


class PathParts(NamedTuple):
    """Named tuple for the path parts.

    These are extracted by the extract_parts_from_path function.

    Attributes:
        year (int | None): The year.
        month (int | None): The month.
        day (int | None): The day.
        slug (str): The slug.
    """

    year: int | None
    month: int | None
    day: int | None
    slug: str


def extract_parts_from_path(path: str) -> PathParts:
    """Extract the parts from the path.

    Args:
        path (str): The path.

    Returns:
        PathParts: The parts extracted from the path.
    """
    # Remove leading and trailing slashes
    path = path.strip("/")

    # Build the regex pattern
    pattern_parts = []

    post_prefix = djpress_settings.POST_PREFIX
    post_permalink = djpress_settings.POST_PERMALINK

    # Add the post prefix to the pattern, if it exists
    if post_prefix:
        pattern_parts.append(re.escape(post_prefix))

    # Add the date parts based on the permalink structure
    if post_permalink:
        if "%Y" in post_permalink:
            post_permalink = post_permalink.replace("%Y", r"(?P<year>\d{4})")
        if "%m" in post_permalink:
            post_permalink = post_permalink.replace("%m", r"(?P<month>\d{2})")
        if "%d" in post_permalink:
            post_permalink = post_permalink.replace("%d", r"(?P<day>\d{2})")
        pattern_parts.append(post_permalink)

    # Add the slug capture group
    pattern_parts.append(r"(?P<slug>[0-9A-Za-z_/-]+)")  # TODO: repeated code - urls.py

    # Join patterns with optional slashes
    pattern = "^" + "/".join(f"(?:{part})" for part in pattern_parts) + "$"

    # Attempt to match the pattern
    match = re.match(pattern, path)

    if not match:
        msg = "Slug could not be found in the provided path."
        raise SlugNotFoundError(msg)

    # Extract the date parts and slug
    year = match.group("year") if "year" in match.groupdict() else None
    month = match.group("month") if "month" in match.groupdict() else None
    day = match.group("day") if "day" in match.groupdict() else None
    slug = match.group("slug") if "slug" in match.groupdict() else None

    if not slug:
        msg = "Slug could not be found in the provided path."
        raise SlugNotFoundError(msg)

    # Convert year, month, day to integers (or None if not present)
    year = int(year) if year else None
    month = int(month) if month else None
    day = int(day) if day else None

    return PathParts(year=year, month=month, day=day, slug=slug)
