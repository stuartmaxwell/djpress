"""Configuration settings for DJ Press."""

import logging

from django.conf import settings as django_settings
from django.core.cache import cache
from django.core.checks import Error, register

from djpress.app_settings import DJPRESS_SETTINGS
from djpress.models.setting import SETTING_CACHE_KEY

logger = logging.getLogger(__name__)

SettingValueType = str | int | bool | list | dict | None


class DJPressSettings:
    """Class to manage DJPress settings."""

    def database_settings_enabled(self) -> bool:
        """Determine if database settings lookups are enabled."""
        # 1. Check Django settings first
        if (
            hasattr(django_settings, "DJPRESS_SETTINGS")
            and "DATABASE_SETTINGS_ENABLED" in django_settings.DJPRESS_SETTINGS
        ):
            val = django_settings.DJPRESS_SETTINGS["DATABASE_SETTINGS_ENABLED"]
            if not isinstance(val, bool):
                msg = f"Expected bool for DATABASE_SETTINGS_ENABLED, got {type(val).__name__}"
                raise TypeError(msg)
            return val

        # 2. Fall back to the app default in app_settings.py
        return DJPRESS_SETTINGS.get("DATABASE_SETTINGS_ENABLED", (False, bool))[0]

    def _get_db_settings(self) -> dict[str, SettingValueType]:
        """Fetch settings from the database, utilizing caching to optimize performance."""
        settings_dict = cache.get(SETTING_CACHE_KEY)

        if settings_dict is None:
            try:
                from djpress.models import Setting  # noqa: PLC0415 # Circular import

                settings_dict = {setting.key: setting.value for setting in Setting.objects.all()}
                cache.set(SETTING_CACHE_KEY, settings_dict, timeout=None)

            except Exception as e:  # noqa: BLE001
                logger.warning(f"Error getting settings from database: {e}")
                # During migrations, bootstrap, or before table is created, return empty dict
                return {}

        return settings_dict

    def __getattr__(self, key: str) -> SettingValueType:
        """Retrieve the setting in order of precedence.

        1. From database settings (if database lookups are enabled and exists)
        2. From Django settings (if exists)
        3. Default from app_settings.py

        Args:
            key (str): The setting to retrieve

        Returns:
            value (SettingValueType): The value of the setting

        Raises:
            AttributeError: If the setting is not defined
            TypeError: If the setting is defined but has the wrong type
            ValueError: If an integer setting is negative
        """
        if key in DJPRESS_SETTINGS:
            expected_type = DJPRESS_SETTINGS[key][1]

            # 1. Check from database settings (if enabled)
            if self.database_settings_enabled():
                db_settings = self._get_db_settings()
                if key in db_settings:
                    value = db_settings[key]
                    if not isinstance(value, expected_type):
                        msg = f"Expected {expected_type.__name__} for {key}, got {type(value).__name__}"
                        raise TypeError(msg)
                    if isinstance(value, int) and value < 0:
                        msg = f"{key} must be greater than or equal to 0."
                        raise ValueError(msg)
                    return value

            # 2. Check if the setting is overridden in Django settings.py
            if hasattr(django_settings, "DJPRESS_SETTINGS") and key in django_settings.DJPRESS_SETTINGS:
                value = django_settings.DJPRESS_SETTINGS[key]
                if not isinstance(value, expected_type):
                    msg = f"Expected {expected_type.__name__} for {key}, got {type(value).__name__}"
                    raise TypeError(msg)
                # Ensure that int types are greater than or equal to 0
                if isinstance(value, int) and value < 0:
                    msg = f"{key} must be greater than or equal to 0."
                    raise ValueError(msg)
                return value

            # 3. Fall back to the default in app_settings.py
            return DJPRESS_SETTINGS[key][0]

        msg = f"Setting {key} is not defined."
        raise AttributeError(msg)


# Singleton instance to use across the application
settings = DJPressSettings()


@register()
def check_djpress_settings(**_) -> list[Error]:  # noqa: ANN003
    """Validate DJPress settings.

    This runs on start up to ensure that the settings are valid.

    Returns:
        None

    Raises:
        ImproperlyConfigured: If any settings are invalid
    """
    errors = []

    if settings.RSS_ENABLED and not settings.RSS_PATH:
        errors.append(
            Error(
                "RSS_PATH cannot be empty if RSS_ENABLED is True.",
                id="djpress.E001",
            ),
        )

    if settings.CATEGORY_ENABLED and not settings.CATEGORY_PREFIX:
        errors.append(
            Error(
                "CATEGORY_PREFIX cannot be empty if CATEGORY_ENABLED is True.",
                id="djpress.E002",
            ),
        )

    if settings.AUTHOR_ENABLED and not settings.AUTHOR_PREFIX:
        errors.append(
            Error(
                "AUTHOR_PREFIX cannot be empty if AUTHOR_ENABLED is True.",
                id="djpress.E003",
            ),
        )

    if settings.TAG_ENABLED and not settings.TAG_PREFIX:
        errors.append(
            Error(
                "TAG_PREFIX cannot be empty if TAG_ENABLED is True.",
                id="djpress.E004",
            ),
        )

    return errors
