"""Custom URL converters."""


class SlugPathConverter:
    """Converter for the DJ Press path.

    The path will only ever contain letters, numbers, underscores, hyphens, and slashes.
    """

    # Regex explained:
    # - [\w/-]+: This matches any word character (alphanumeric or underscore), hyphen, or slash, one or more times.
    regex = r"[\w/-]+"

    def to_python(self, value: str) -> str:
        """Return the value as a string."""
        return str(value)

    def to_url(self, value: str) -> str:
        """Return the value as a string."""
        return str(value)
