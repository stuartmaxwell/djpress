"""Handlers that execute the callbacks."""

import logging
from typing import TYPE_CHECKING

from django.db import models

if TYPE_CHECKING:
    from djpress.models import Post
    from djpress.plugins.protocols import ContentTransformer, PostObjectProvider, SearchProvider, SimpleContentProvider

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
    value: str | None = None,
) -> str:
    """Runs a `SimpleContentProvider` callback and concatenates the results.

    Args:
        callback: The `SimpleContentProvider` callback.
        value: The previous content (if any).

    Returns:
        The generated `str` content concatenated with the previous value.
    """
    previous_content = value if value else ""
    result = ""
    try:
        result = callback()
    except Exception as exc:  # noqa: BLE001
        msg = f"Error running callback {callback}. Callback skipped: {exc}"
        logger.warning(msg)

    return f"{previous_content}{result}" if result else previous_content


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


def _run_search_provider(
    callback: "SearchProvider",
    value: str | models.QuerySet,
) -> "models.QuerySet[Post] | str | None":
    """Runs a `SearchProvider` callback.

    If a previous callback already returned a QuerySet, we return that and skip the current callback.
    This ensures that multiple search plugins don't crash when they expect a string query.

    Args:
        callback: The `SearchProvider` callback.
        value: The search query (str) or a previous QuerySet results.

    Returns:
        The search results (QuerySet), or the original query if no results yet.
    """
    # If we already have a QuerySet from a previous plugin, just return it.
    if isinstance(value, models.QuerySet):
        logger.debug(f"Callback '{callback}' received a QuerySet, not attempting to search again.")
        return value

    try:
        results = callback(value)
    except Exception as exc:  # noqa: BLE001
        msg = f"Error running callback '{callback}'. Callback skipped: {exc}"
        logger.warning(msg)
        return value

    if not isinstance(results, models.QuerySet):
        logger.debug(f"Callback '{callback}' did not return a QuerySet.")
        return value

    return results
