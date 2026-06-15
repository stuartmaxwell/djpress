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
        callback: The callback function, method, or callable object to validate.

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    protocol = hook.protocol
    if protocol is None:
        return False, f"No protocol defined for hook {hook.name}"

    if not callable(callback):
        return False, "Callback is not callable."

    try:
        protocol_sig = inspect.signature(protocol.__call__)
        protocol_params = list(protocol_sig.parameters.values())[1:]  # skip self for protocol

        callback_sig = inspect.signature(callback)
        callback_params = list(callback_sig.parameters.values())

        # Check parameter counts (allowing callbacks to have optional params with default values)
        required_params = [p for p in callback_params if p.default is inspect.Parameter.empty]

        if len(required_params) > len(protocol_params):
            return (
                False,
                f"Callback requires {len(required_params)} parameters, but hook only provides {len(protocol_params)}",
            )

        # Parameter validation
        for p_param, c_param in zip(protocol_params, callback_params, strict=False):
            p_type = p_param.annotation
            c_type = c_param.annotation

            # Allow the callback to omit annotations (empty) or use Any
            if c_type is inspect.Parameter.empty or c_type is Any:
                continue

            # Standardise types to strings for comparison to handle forward references
            p_type_str = p_type if isinstance(p_type, str) else getattr(p_type, "__name__", str(p_type))
            c_type_str = c_type if isinstance(c_type, str) else getattr(c_type, "__name__", str(c_type))

            # Treat "object" as compatible with anything
            if c_type_str == "object":
                continue

            if p_type_str != c_type_str:
                return False, (
                    f"Parameter type mismatch: expected {p_type_str}, got {c_type_str} "
                    f"for parameter '{c_param.name}' in hook '{hook.name}'"
                )

    except Exception as exc:  # noqa: BLE001
        return False, f"Signature validation error: {exc}"
    return True, ""


# Define hooks
PRE_RENDER_CONTENT = _Hook("pre_render_content", ContentTransformer)
POST_RENDER_CONTENT = _Hook("post_render_content", ContentTransformer)
DJPRESS_HEADER = _Hook("djpress_header", SimpleContentProvider)
DJPRESS_FOOTER = _Hook("djpress_footer", SimpleContentProvider)
POST_SAVE_POST = _Hook("post_save_post", PostObjectProvider)
SEARCH_CONTENT = _Hook("search_content", SearchProvider)
