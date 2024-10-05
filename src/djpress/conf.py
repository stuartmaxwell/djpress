"""Configuration settings for DJ Press."""

from django.conf import settings as django_settings

from djpress.app_settings import DJPRESS_SETTINGS

SettingValueType = str | int | bool | list | dict | None


class DJPressSettings:
    """Class to manage DJPress settings."""

    def __getattr__(self, key: str) -> SettingValueType:
        """Retrieve the setting in order of precedence.

        1. From Django settings (if exists)
        2. Default from app_settings.py

        Args:
            key (str): The setting to retrieve

        Returns:
            value (SettingValueType): The value of the setting

        Raises:
            AttributeError: If the setting is not defined
            TypeError: If the setting is defined but has the wrong type
        """
        # Check if the setting is overridden in Django settings.py
        # If so, validate the type and return the value
        if hasattr(django_settings, "DJPRESS_SETTINGS") and key in django_settings.DJPRESS_SETTINGS:
            value = django_settings.DJPRESS_SETTINGS[key]
            expected_type = DJPRESS_SETTINGS[key][1]
            if not isinstance(value, expected_type):
                msg = f"Expected {expected_type.__name__} for {key}, got {type(value).__name__}"
                raise TypeError(msg)
            return value

        # If no override, fall back to the default in app_settings.py
        if key in DJPRESS_SETTINGS:
            return DJPRESS_SETTINGS[key][0]

        msg = f"Setting {key} is not defined."
        raise AttributeError(msg)


# Singleton instance to use across the application
settings = DJPressSettings()
