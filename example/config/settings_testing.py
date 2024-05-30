"""Django settings for running tests."""

from .settings import *  # noqa: F403, F401, RUF100

# Use an in-memory database for testing
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}

# DJPress settings
TRUNCATE_TAG = "<!--more-->"
CACHE_CATEGORIES: bool = True
CACHE_RECENT_PUBLISHED_POSTS: bool = False
RECENT_PUBLISHED_POSTS_COUNT: int = 20
MARKDOWN_EXTENSIONS: list = ["fenced_code", "codehilite", "tables"]
BLOG_TITLE: str = "My DJ Press Blog"

# DJPress URL settings
CATEGORY_PATH_ENABLED: bool = True
CATEGORY_PATH: str = "category"
AUTHOR_PATH_ENABLED: bool = True
AUTHOR_PATH: str = "author"
ARCHIVES_PATH_ENABLED: bool = True
ARCHIVES_PATH: str = "archives"
DATE_ARCHIVES_ENABLED: bool = True
RSS_ENABLED: bool = True
RSS_PATH: str = "rss"

# The following are used to generate the post permalink
DAY_SLUG: str = "%Y/%m/%d"
MONTH_SLUG: str = "%Y/%m"
YEAR_SLUG: str = "%Y"
POST_PREFIX: str = "post"
POST_PERMALINK: str = ""
