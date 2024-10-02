"""Utils that are used in the urls.py file.

These are only loaded when the urls.py is loaded - typically only at startup.
"""

import re

from djpress.conf import settings


def post_prefix_to_regex(prefix: str) -> str:
    """Convert the post prefix to a regex pattern.

    Args:
        prefix (str): The post prefix that is configured in the settings.

    Returns:
        str: The regex pattern.
    """
    regex_parts = []

    # Regexes are complicated - this is what the following does:
    # - `(...)`: The parentheses create a capturing group. This means that the splits will occur around these matches,
    #   but the matches themselves will be included in the resulting list.
    # - `\{\{`: This matches two opening curly braces {{. The backslashes are necessary because curly braces have
    #   special meaning in regex, so we need to escape them to match literal curly braces.
    # - `.*?`: This is matches the characters inside the curly brackets.
    #   - `.`: Matches any single character.
    #   - `*`: Means "zero or more" of the preceding pattern.
    #   - `?`: Makes the `*` non-greedy, meaning it will match as few characters as possible.
    # - `\}\}`: This matches two closing curly braces }}, again escaped with backslashes.
    parts = re.split(r"(\{\{.*?\}\})", prefix)

    for part in parts:
        if part == "{{ year }}":
            regex_parts.append(r"(?P<year>\d{4})")
        elif part == "{{ month }}":
            regex_parts.append(r"(?P<month>\d{2})")
        elif part == "{{ day }}":
            regex_parts.append(r"(?P<day>\d{2})")
        else:
            # Escape the part, but replace escaped spaces with regular spaces
            escaped_part = re.escape(part).replace("\\ ", " ")
            regex_parts.append(escaped_part)

    regex = "".join(regex_parts)

    # If the regex is blank we return just the slug re, otherwise we append a slash and the slug re
    if not regex:
        return r"(?P<slug>[\w-]+)"

    return rf"{regex}/(?P<slug>[\w-]+)"


def regex_archives() -> str:
    """Generate the regex path for the archives view.

    The following regex is used to match the archives path. It is used to match
    the following patterns:
    - 2024
    - 2024/01
    - 2024/01/01
    There will always be a year.
    If there is a month, there will always be a year.
    If there is a day, there will always be a month and a year.
    """
    regex = r"(?P<year>\d{4})(?:/(?P<month>\d{2})(?:/(?P<day>\d{2}))?)?$"

    if settings.ARCHIVE_PREFIX:
        regex = rf"{settings.ARCHIVE_PREFIX}/{regex}"

    if settings.APPEND_SLASH:
        return regex[:-1] + "/$"
    return regex


def regex_page() -> str:
    """Generate the regex path for pages.

    The following regex is used to match the path. It is used to match the
    any path that contains letters, numbers, underscores, hyphens, and slashes.
    """
    regex = r"^(?P<path>[0-9A-Za-z/_-]*)$"
    if settings.APPEND_SLASH:
        return regex[:-1] + "/$"
    return regex
