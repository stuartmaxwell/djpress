"""Protocols to define behaviour for the hook types in the DJPress plugin system."""

import logging
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from djpress.plugins.handlers import _run_content_provider, _run_content_transformer, _run_object_provider

if TYPE_CHECKING:
    from djpress.models import Post

logger = logging.getLogger(__name__)


@runtime_checkable
class ContentTransformer(Protocol):
    """Protocol for hooks that transform content.

    Args:
        content: The content to transform.

    Returns:
        The transformed content.
    """

    handler = _run_content_transformer

    def __call__(self, content: str) -> str:
        """Transform content and return the result."""
        ...  # pragma: no cover


@runtime_checkable
class SimpleContentProvider(Protocol):
    """Protocol for hooks that provide simple content (no arguments).

    Returns:
        The generated content.
    """

    handler = _run_content_provider

    def __call__(self) -> str:
        """Generate static content."""
        ...  # pragma: no cover


@runtime_checkable
class PostObjectProvider(Protocol):
    """Protocol for hooks that run after a post is saved.

    Args:
        post: The post object that was saved.

    Returns:
        None
    """

    handler = _run_object_provider

    def __call__(self, post: "Post") -> "Post":
        """Run logic after a post is saved."""
        ...  # pragma: no cover
