"""Django settings for running tests."""

from .settings import *  # noqa: F403, F401, RUF100

# Use an in-memory database for testing
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}

# Changing these settings will affect lots of tests!
BLOG_TITLE = "My Test DJ Press Blog"
AUTHOR_PATH_ENABLED = True
AUTHOR_PATH = "test-url-author"
CATEGORY_PATH_ENABLED = True
CATEGORY_PATH = "test-url-category"
POST_PREFIX = "test-posts"
POST_PERMALINK = ""
MARKDOWN_EXTENSIONS = ["fenced_code", "codehilite", "tables"]
TRUNCATE_TAG = "<!--test-more-->"
CACHE_RECENT_PUBLISHED_POSTS = False
CACHE_CATEGORIES = True
RECENT_PUBLISHED_POSTS_COUNT = 3
DATE_ARCHIVES_ENABLED = True
