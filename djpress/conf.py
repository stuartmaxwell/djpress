"""Configuration settings for DJ Press."""

from django.conf import settings as django_settings

from . import app_settings as default_settings


class Settings:
    """Class to manage DJ Press settings."""

    def __init__(
        self: "Settings",
        default_settings_module: object,
        user_settings_module: object,
    ) -> None:
        """Initialize the settings object."""
        self._default_settings = default_settings_module
        self._user_settings = user_settings_module

    def __getattr__(self: "Settings", name: str) -> object:
        """Get the value of a setting."""
        # If the setting is found in the user settings, return it
        if hasattr(self._user_settings, name):
            return getattr(self._user_settings, name)
        # If the setting is found in the default settings, return it
        if hasattr(self._default_settings, name):
            return getattr(self._default_settings, name)
        # If the setting is not found in either, raise an AttributeError
        msg = f"Setting '{name}' not found"
        raise AttributeError(msg)


settings = Settings(default_settings, django_settings)
