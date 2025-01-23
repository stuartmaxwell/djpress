"""Custom URL converters."""

from django.conf import settings


class SlugPathConverter:
    """Converter for the DJ Press path.

    The path will only ever contain letters, numbers, underscores, hyphens, pluses, and slashes.
    """

    # Regex explained:
    # - [\w/-]+: This matches any word character (alphanumeric or underscore), hyphen, or slash, one or more times.
    @property
    def regex(self) -> str:
        """Return the regex for the path."""
        the_regex = r"[\w/+-]+"

        if settings.APPEND_SLASH:
            return rf"^{the_regex}/$"

        return rf"^{the_regex}$"

    def to_python(self, value: str) -> str:
        """Return the value as a string."""
        return str(value)

    def to_url(self, value: str) -> str:
        """Return the value as a string."""
        return str(value)
