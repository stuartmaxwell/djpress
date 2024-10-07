"""Custom exceptions for the djpress package."""


class PostNotFoundError(Exception):
    """Exception raised when the post is not found in the database."""


class PageNotFoundError(Exception):
    """Exception raised when the page is not found in the database."""
