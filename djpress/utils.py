"""Utility functions that are used in the project."""

import markdown
from django.contrib.auth.models import User
from django.utils.timezone import datetime

from djpress.conf import settings

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
            datetime(int_year, int_month, int_day)

        elif int_month:
            datetime(int_year, int_month, 1)

        else:
            datetime(int_year, 1, 1)

    except ValueError as exc:
        msg = "Invalid date"
        raise ValueError(msg) from exc
