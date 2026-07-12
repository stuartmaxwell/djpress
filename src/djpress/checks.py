"""Custom checks for DJPress."""

from django.conf import settings as django_settings
from django.core.checks import Tags, Warning, register  # noqa: A004

from djpress.app_settings import DEPRECATED_SETTINGS
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


@register()
def check_deprecated_settings(**_) -> list[Warning]:  # noqa: ANN003
    """Checks for deprecated settings still being used."""
    found = []
    configured = getattr(django_settings, "DJPRESS_SETTINGS", {})
    for old, new in DEPRECATED_SETTINGS.items():
        if old in configured:
            found.append(
                Warning(
                    f"The DJPress setting {old} is deprecated and will be removed in a future release.",
                    hint=f"Rename {old} to {new} in DJPRESS_SETTINGS.",
                    id="djpress.W001",
                ),
            )
    return found
