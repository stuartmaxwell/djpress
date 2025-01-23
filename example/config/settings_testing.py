"""Django settings for running tests."""

from .settings import *  # noqa: F403, F401, RUF100

# Use an in-memory database for testing
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}

PASSWORD_HASHERS: list[str] = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

# Changing these settings will affect lots of tests!
DJPRESS_SETTINGS = {
    "SITE_TITLE": "My Test DJ Press Blog",
    "SITE_DESCRIPTION": "This is a test blog.",
    "ARCHIVE_PREFIX": "test-url-archives",
    "ARCHIVE_ENABLED": True,
    "AUTHOR_ENABLED": True,
    "AUTHOR_PREFIX": "test-url-author",
    "CATEGORY_ENABLED": True,
    "CATEGORY_PREFIX": "test-url-category",
    "POST_PREFIX": "test-posts",
    "TRUNCATE_TAG": "<!--test-more-->",
    "CACHE_RECENT_PUBLISHED_POSTS": False,
    "CACHE_CATEGORIES": True,
    "RECENT_PUBLISHED_POSTS_COUNT": 3,
    "POST_READ_MORE_TEXT": "Test read more...",
    "RSS_PATH": "test-rss",
    "TAG_ENABLED": True,
    "TAG_PREFIX": "test-url-tag",
}
