"""Djpress app configuration."""

from django.apps import AppConfig
from django.core.checks import Tags, register


class DjpressConfig(AppConfig):
    """Djpress app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "djpress"
    label = "djpress"

    def ready(self) -> None:
        """Run when the app is ready."""
        # Import signals to ensure they are registered
        import djpress.signals  # noqa: F401

        # Initialize plugin system
        from djpress.plugins import registry

        registry.load_plugins()

        # Register check explicitly
        from djpress.checks import check_plugin_hooks

        register(check_plugin_hooks, Tags.compatibility)
