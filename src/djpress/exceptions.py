"""Custom exceptions for the djpress package."""


class SlugNotFoundError(Exception):
    """Exception raised when the slug is missing from the URL path."""
