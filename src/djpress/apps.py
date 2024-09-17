"""Djpress app configuration."""

from django.apps import AppConfig


class DjpressConfig(AppConfig):
    """Djpress app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "djpress"
    label = "djpress"

    def ready(self: "DjpressConfig") -> None:
        """Import signals."""
        import djpress.signals  # noqa: F401
