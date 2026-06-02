"""Setting model for storing dynamic settings in the database."""

from django.core.exceptions import ValidationError
from django.db import models

from djpress.app_settings import DJPRESS_SETTINGS

SETTING_CACHE_KEY = "djpress:settings"


class Setting(models.Model):
    """Model for storing dynamic settings in the database."""

    key = models.CharField(max_length=255, unique=True)
    value = models.JSONField(null=True, blank=True)

    class Meta:
        """Meta options for the Setting model."""

        verbose_name = "setting"
        verbose_name_plural = "settings"

    def __str__(self) -> str:
        """Return the string representation of the setting."""
        return f"{self.key}: {self.value}"

    def save(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        """Override save to force full clean before saving."""
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self) -> None:
        """Validate that the setting configuration is correct and safe."""
        if self.key == "DATABASE_SETTINGS_ENABLED":
            msg = "DATABASE_SETTINGS_ENABLED is a system-level setting and can only be configured in settings.py."
            raise ValidationError(msg)

        if self.key in DJPRESS_SETTINGS:
            expected_type = DJPRESS_SETTINGS[self.key][1]
            if not isinstance(self.value, expected_type):
                msg = (
                    f"Invalid type for setting '{self.key}'. "
                    f"Expected {expected_type.__name__}, "
                    f"got {type(self.value).__name__}."
                )
                raise ValidationError(msg)

            if isinstance(self.value, int) and self.value < 0:
                msg = f"Setting '{self.key}' must be greater than or equal to 0."
                raise ValidationError(msg)
