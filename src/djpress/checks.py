"""Custom checks for DJPress."""

from django.core.checks import Tags, Warning, register

from djpress.plugins import registry


@register(Tags.compatibility)
def check_plugin_loading(app_configs, **kwargs) -> list[Warning]:  # noqa: ANN001, ANN003, ARG001
    """Report any plugin loading warnings."""
    warnings = []

    for plugin_error in registry.plugin_errors:
        warning = Warning(
            f"Plugin loading error: {plugin_error}",
            id="djpress.W001",
        )
        warnings.append(warning)

    return warnings
