"""Radically simplified hook system using function introspection."""

import inspect
from collections.abc import Callable  # Modern import for Callable
from typing import Any

from djpress.plugins.protocols import ContentTransformer, PostObjectProvider, SearchProvider, SimpleContentProvider


class _Hook:
    """A single plugin hook definition, including name, protocol, and handler."""

    def __init__(self, name: str, protocol: type[object]) -> None:
        """Initialize a Hook with a name and protocol.

        Args:
            name: The string name of the hook (for config/logging).
            protocol: The protocol class defining the hook signature.
        """
        self.name = name
        self.protocol = protocol

    def __eq__(self, other: object) -> bool:
        """Check equality based on hook name.

        Args:
            other: The object to compare.

        Returns:
            True if the other object is a Hook with the same name, else False.
        """
        if not isinstance(other, _Hook):
            return NotImplemented
        return self.name == other.name

    def __hash__(self) -> int:
        """Return a hash based on the hook name.

        This method makes _Hook instances hashable, allowing them to be used as keys in dictionaries
        (e.g., in PluginRegistry.hooks) or elements in sets. The hash is derived from the hook's 'name' attribute.

        This implementation ensures that if two _Hook instances are considered equal by __eq__
        (i.e., they have the same name), they will also have the same hash value.

        Returns:
            The integer hash of the hook's name.
        """
        return hash(self.name)


def _validate_hook_callback(hook: _Hook, callback: Callable[..., Any]) -> tuple[bool, str]:
    """Validate that a callback matches the expected protocol signature for a hook.

    Intended for use by PluginRegistry during hook registration. Not part of the public plugin authoring API.

    Args:
        hook: The _Hook object representing the hook point.
        callback: The callback function or method to validate.

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    protocol = hook.protocol
    if protocol is None:
        return False, f"No protocol defined for hook {hook.name}"

    try:
        protocol_sig = inspect.signature(protocol.__call__)
        protocol_params = list(protocol_sig.parameters.values())[1:]  # skip self for protocol

        # For functions and methods, self is already bound (not present in signature)
        if inspect.isfunction(callback) or inspect.ismethod(callback):
            callback_sig = inspect.signature(callback)
            callback_params = list(callback_sig.parameters.values())
        else:
            return False, "Callback is expected to be a method or function."

        if len(protocol_params) != len(callback_params):
            return False, f"Expected {len(protocol_params)} parameters, got {len(callback_params)}"

        # Parameter type hint validation
        for p_param, c_param in zip(protocol_params, callback_params, strict=False):
            p_type = p_param.annotation
            c_type = c_param.annotation

            if p_type != c_type:
                return False, (
                    f"Parameter type mismatch: expected {p_type}, got {c_type} "
                    f"for parameter '{c_param.name}' in hook '{hook.name}'"
                )

    except Exception as exc:  # noqa: BLE001
        return False, f"Signature validation error: {exc}"
    return True, ""


# Define hooks
PRE_RENDER_CONTENT = _Hook("pre_render_content", ContentTransformer)
POST_RENDER_CONTENT = _Hook("post_render_content", ContentTransformer)
DJ_HEADER = _Hook("dj_header", SimpleContentProvider)
DJ_FOOTER = _Hook("dj_footer", SimpleContentProvider)
POST_SAVE_POST = _Hook("post_save_post", PostObjectProvider)
SEARCH_CONTENT = _Hook("search_content", SearchProvider)
