"""URL patterns for the djpress application."""

import re

from django.conf import settings as django_settings
from django.contrib.auth.models import User

from djpress.conf import settings as djpress_settings
from djpress.models.post import Category, Post, Tag


def regex_post() -> str:
    """Convert the post prefix to a regex pattern.

    This will match the following URL parts:
    - The year in the format of 4 digits.
    - The month in the format of 2 digits.
    - The day in the format of 2 digits.
    - The slug in the format of word characters or hyphens.

    Args:
        prefix (str): The post prefix that is configured in the settings.

    Returns:
        str: The regex pattern.
    """
    prefix = djpress_settings.POST_PREFIX
    if not isinstance(prefix, str):  # pragma: no cover
        msg = f"Expected string for POST_PREFIX, got {type(prefix).__name__}"
        raise TypeError(msg)

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
        # Remove spaces from the part so that either {{ year }} or {{year}} will work
        if part.replace(" ", "") == "{{year}}":
            regex_parts.append(r"(?P<year>\d{4})")
        elif part.replace(" ", "") == "{{month}}":
            regex_parts.append(r"(?P<month>\d{2})")
        elif part.replace(" ", "") == "{{day}}":
            regex_parts.append(r"(?P<day>\d{2})")
        else:
            # Escape the part, but replace escaped spaces with regular spaces
            escaped_part = re.escape(part).replace("\\ ", " ")
            regex_parts.append(escaped_part)

    regex = "".join(regex_parts)

    # If the regex is blank we return just the slug re, otherwise we append a slash and the slug re
    # Regex explanation:
    # - (?P<slug>...): This is a named capture group.
    # - [\w-]: This matches any word character (alphanumeric or underscore) or a hyphen.
    # - +: This means "one or more" of the preceding pattern.
    if not regex:
        return r"(?P<slug>[\w-]+)"

    return rf"{regex}/(?P<slug>[\w-]+)"


def get_post_url(post: Post) -> str:
    """Return the URL for the post."""
    prefix = djpress_settings.POST_PREFIX
    if not isinstance(prefix, str):  # pragma: no cover
        msg = f"Expected POST_PREFIX to be a string, got {type(prefix).__name__}"
        raise TypeError(msg)

    # Remove spaces from the prefix so that either {{ year }} or {{year}} will work
    prefix = prefix.replace(" ", "")

    post_date = post._date  # noqa: SLF001

    if post_date is None:
        msg = "Post date is not set. Cannot generate URL."
        raise ValueError(msg)

    # Replace the placeholders in the prefix with the actual values
    if "{{year}}" in prefix:
        prefix = prefix.replace("{{year}}", post_date.strftime("%Y"))
    if "{{month}}" in prefix:
        prefix = prefix.replace("{{month}}", post_date.strftime("%m"))
    if "{{day}}" in prefix:
        prefix = prefix.replace("{{day}}", post_date.strftime("%d"))

    url = f"/{post.slug}" if prefix == "" else f"/{prefix}/{post.slug}"

    if django_settings.APPEND_SLASH:
        return f"{url}/"

    return url


def regex_archives() -> str:
    """Generate the regex path for the archives view.

    The following regex is used to match the archives path. It is used to match
    the following patterns:
    - 2024
    - 2024/01
    - 2024/01/01

    Returns:
        str: The regex pattern.
    """
    archive_prefix = djpress_settings.ARCHIVE_PREFIX
    if not isinstance(archive_prefix, str):  # pragma: no cover
        msg = f"Expected ARCHIVE_PREFIX to be a string, got {type(archive_prefix).__name__}"
        raise TypeError(msg)

    # Regex explanation:
    # - (?P<year>\d{4}): Required - this matches the year in the format of 4 digits.
    # - (/(?P<month>\d{2}))?: Optional - this matches the month in the format of 2 digits.
    # - (/(?P<day>\d{2}))?: Optional - this matches the day in the format of 2 digits.
    regex = r"(?P<year>\d{4})(/(?P<month>\d{2}))?(/(?P<day>\d{2}))?"

    if djpress_settings.ARCHIVE_PREFIX:
        regex = rf"{re.escape(archive_prefix)}/{regex}"

    return regex


def regex_page() -> str:
    """Generate the regex path for pages.

    The following regex is used to match the path. It is used to match the
    any path that contains letters, numbers, underscores, hyphens, and slashes.
    """
    # Regex explanation:
    # - (?P<path>([\w-]+/)*[\w-]+): This matches the path.
    #   - (?P<path>...): This is a named capture group.
    #   - ([\w-]+/)*: This matches any word character (alphanumeric or underscore) or a hyphen, followed by a slash.
    #     - [\w-]: This matches any word character (alphanumeric or underscore) or a hyphen.
    #     - +: This means "one or more" of the preceding pattern.
    return r"(?P<path>([\w-]+/)*[\w-]+)"


def regex_category() -> str:
    """Generate the regex path for the category view.

    The category URL must have the CATEGORY_PREFIX. If not, an error occurs on startup: E002. See conf.py for details.
    """
    category_prefix = djpress_settings.CATEGORY_PREFIX
    if not isinstance(category_prefix, str):  # pragma: no cover
        msg = f"Expected CATEGORY_PREFIX to be a string, got {type(category_prefix).__name__}"
        raise TypeError(msg)

    # Regex explanation:
    # - (?P<slug>[\w-]+): This is a named capture group that matches any word character (alphanumeric or underscore)
    #   or a hyphen.
    regex = r"(?P<slug>[\w-]+)"

    return rf"{re.escape(category_prefix)}/{regex}"


def regex_tag() -> str:
    """Generate the regex path for the tag view.

    Needs to match the following patterns:

    - slug
    - slug1+slug2
    - slug1+slug2+slug3
    - etc...

    The entire slug is captured in the slug group - i.e. if there's one tag, the slug is just that tag, but if there's
    more than one tag, the slug is all the tags joined by a plus sign.

    The tag URL must have the TAG_PREFIX. If not, an error occurs on startup: E004. See conf.py for details.
    """
    tag_prefix = djpress_settings.TAG_PREFIX
    if not isinstance(tag_prefix, str):  # pragma: no cover
        msg = f"Expected TAG_PREFIX to be a string, got {type(tag_prefix).__name__}"
        raise TypeError(msg)

    # Regex explanation:
    # - (?P<slug> )   This is a named capture group called slug
    # - [\w-]+        This matches any word character (alphanumeric or underscore) or a hyphen, one or more times
    # - (?:\+[\w-]+)* This is a non-capturing group that matches a plus sign followed by any word character or hyphen,
    #                 one or more times. This group can be repeated zero or more times.
    regex = r"(?P<slug>[\w-]+(?:\+[\w-]+)*)"

    return rf"{re.escape(tag_prefix)}/{regex}"


def regex_author() -> str:
    """Generate the regex path for the author view."""
    author_prefix = djpress_settings.AUTHOR_PREFIX
    if not isinstance(author_prefix, str):  # pragma: no cover
        msg = f"Expected AUTHOR_PREFIX to be a string, got {type(author_prefix).__name__}"
        raise TypeError(msg)

    # Regex explanation:
    # - (?P<author>[\w-]+): This is a named capture group that matches any word character (alphanumeric or underscore)
    #   or a hyphen.
    regex = r"(?P<author>[\w-]+)"

    if djpress_settings.AUTHOR_PREFIX:
        regex = rf"{re.escape(author_prefix)}/{regex}"

    return regex


def get_path_regex(path_match: str) -> str:
    """Return the regex for the requested match."""
    if path_match == "post":
        regex = regex_post()
    if path_match == "archives":
        regex = regex_archives()
    if path_match == "page":
        regex = regex_page()
    if path_match == "category":
        regex = regex_category()
    if path_match == "tag":
        regex = regex_tag()
    if path_match == "author":
        regex = regex_author()

    if django_settings.APPEND_SLASH:
        return f"^{regex}/$"

    return f"^{regex}$"


def get_author_url(user: User) -> str:
    """Return the URL for the author's page."""
    url = (
        f"/{djpress_settings.AUTHOR_PREFIX}/{user.username}"
        if djpress_settings.AUTHOR_PREFIX
        else f"/author/{user.username}"
    )

    if django_settings.APPEND_SLASH:
        return f"{url}/"

    return url


def get_category_url(category: "Category") -> str:
    """Return the URL for the category.

    If either djpress_settings.CATEGORY_ENABLED or djpress_settings.CATEGORY_PREFIX is not set, return an empty string.
    """
    if djpress_settings.CATEGORY_ENABLED and djpress_settings.CATEGORY_PREFIX != "":
        url = f"/{djpress_settings.CATEGORY_PREFIX}/{category.slug}"
    else:
        url = ""

    if django_settings.APPEND_SLASH:
        return f"{url}/"

    return url


def get_tag_url(tag: "Tag") -> str:
    """Return the URL for a single tag."""
    if djpress_settings.TAG_ENABLED and djpress_settings.TAG_PREFIX != "":
        url = f"/{djpress_settings.TAG_PREFIX}/{tag.slug}"
    else:
        url = ""

    if django_settings.APPEND_SLASH:
        return f"{url}/"

    return url


def get_archives_url(year: int, month: int | None = None, day: int | None = None) -> str:
    """Return the URL for the archives page."""
    url = f"/{djpress_settings.ARCHIVE_PREFIX}/{year}" if djpress_settings.ARCHIVE_PREFIX else f"/{year}"

    if month:
        url += f"/{month:02d}"
    if day:
        url += f"/{day:02d}"

    if django_settings.APPEND_SLASH:
        return f"{url}/"

    return url


def get_page_url(page: Post) -> str:
    """Return the URL for the page."""
    url = f"/{page.full_page_path}"

    if django_settings.APPEND_SLASH:
        return f"{url}/"

    return url


def get_rss_url() -> str:
    """Return the URL for the RSS feed.

    If the RSS path is not set, the default is "/feed". This will raise an error if the path is not set.

    Returns:
        str: The URL for the RSS feed.
    """
    url = f"/{djpress_settings.RSS_PATH}"

    if django_settings.APPEND_SLASH:
        return f"{url}/"

    return url
