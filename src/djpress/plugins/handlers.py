"""Handlers that execute the callbacks."""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from djpress.models import Post
    from djpress.plugins.protocols import ContentTransformer, PostObjectProvider, SimpleContentProvider

logger = logging.getLogger(__name__)


def _run_content_transformer(
    callback: "ContentTransformer",
    value: str,
) -> object:
    """Chain ContentTransformer callbacks (single-argument, returns value).

    Args:
        callback: The `ContentTransformer` callback.
        value: The `str` object to transform.

    Returns:
        The final transformed content, or the original value.
    """
    original_value = value
    result = None
    try:
        result = callback(content=value)
    except Exception as exc:  # noqa: BLE001
        msg = f"Error running callback {callback}. Callback skipped: {exc}"
        logger.warning(msg)

    return result if result else original_value


def _run_content_provider(
    callback: "SimpleContentProvider",
    value: None = None,
) -> str:
    """Runs a `SimpleContentProvider` callback..

    Args:
        callback: The `SimpleContentProvider` callback.
        value: No arguments expected.

    Returns:
        The generated `str` content, or an empty string.
    """
    _original_value = value
    result = ""
    try:
        result = callback()
    except Exception as exc:  # noqa: BLE001
        msg = f"Error running callback {callback}. Callback skipped: {exc}"
        logger.warning(msg)

    return result if result else ""


def _run_object_provider(
    callback: "PostObjectProvider",
    value: "Post",
) -> "Post":
    """Receives an object, and passes back the original object.

    Args:
        callback: The `PostObjectProvider` callback functions.
        value: The `Post` object to pass to the callback.

    Returns:
        The original `Post` object.
    """
    original_post = value
    try:
        callback(value)
    except Exception as exc:  # noqa: BLE001
        msg = f"Error running callback '{callback}'. Callback skipped: {exc}"
        logger.warning(msg)

    return original_post
