"""Configuration settings for DJ Press."""

from typing import Any

from django.conf import settings as django_settings
from django.core.cache import cache

from djpress import app_settings as default_settings


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

    def __getattr__(self: "Settings", name: str) -> Any:  # noqa: ANN401
        """Get the value of a setting.

        Args:
            name (str): The name of the setting to get.

        Returns:
            Any: The value of the setting.

        Raises:
            AttributeError: If the setting is not found.
        """
        # If the setting is found in the user settings, return it
        if hasattr(self._user_settings, name):
            return getattr(self._user_settings, name)
        # If the setting is found in the default settings, return it
        if hasattr(self._default_settings, name):
            return getattr(self._default_settings, name)
        # If the setting is not found in either, raise an AttributeError
        msg = f"Setting '{name}' not found"
        raise AttributeError(msg)

    def set(self: "Settings", name: str, value: object) -> None:
        """Set the value of a setting and invalidate the cache if necessary.

        Right now this is only used by pytest, but in the future, this will be the
        correct way to set a setting value.
        """
        setattr(self._user_settings, name, value)
        if self._should_invalidate_cache():
            cache.clear()

    def _should_invalidate_cache(self: "Settings") -> bool:
        """Check if cache should be invalidated based on cache settings."""
        return self.cache_categories or self.cache_recent_published_posts

    @property
    def cache_categories(self: "Settings") -> bool:
        """Return the value of the CACHE_CATEGORIES setting."""
        return getattr(
            self._user_settings,
            "CACHE_CATEGORIES",
            getattr(self._default_settings, "CACHE_CATEGORIES", True),
        )

    @property
    def cache_recent_published_posts(self: "Settings") -> bool:
        """Return the value of the CACHE_RECENT_PUBLISHED_POSTS setting."""
        return getattr(
            self._user_settings,
            "CACHE_RECENT_PUBLISHED_POSTS",
            getattr(self._default_settings, "CACHE_RECENT_PUBLISHED_POSTS", False),
        )


settings = Settings(default_settings, django_settings)
