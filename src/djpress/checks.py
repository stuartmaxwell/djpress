"""Custom checks for DJPress."""

from django.core.checks import Warning


def check_plugin_hooks(app_configs, **kwargs) -> list[Warning]:  # noqa: ANN001, ANN003, ARG001
    """Check for unknown plugin hooks."""
    from djpress.plugins import Hooks, registry

    # Ensure plugins are loaded
    if not registry._loaded:  # noqa: SLF001
        registry.load_plugins()

    warnings = []

    for hook_name in registry.hooks:
        if not isinstance(hook_name, Hooks):
            warning = Warning(
                f"Plugin registering unknown hook '{hook_name}'.",
                hint=("This might indicate use of a deprecated hook or a hook from a newer version of DJPress."),
                obj=hook_name,
                id="djpress.W001",
            )
            warnings.append(warning)

    return warnings
