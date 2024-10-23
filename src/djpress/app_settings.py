"""Settings file for DJ Press."""

# DJPress settings
DJPRESS_SETTINGS = {
    "TRUNCATE_TAG": ("<!--more-->", str),
    "CACHE_CATEGORIES": (True, bool),
    "CACHE_RECENT_PUBLISHED_POSTS": (False, bool),
    "RECENT_PUBLISHED_POSTS_COUNT": (20, int),
    "MARKDOWN_EXTENSIONS": ([], list),
    "MARKDOWN_EXTENSION_CONFIGS": ({}, dict),
    "BLOG_TITLE": ("My DJ Press Blog", str),
    "BLOG_DESCRIPTION": ("", str),
    "POST_READ_MORE_TEXT": ("Read more...", str),
    "POST_PREFIX": ("{{ year }}/{{ month }}/{{ day }}", str),
    "ARCHIVE_ENABLED": (True, bool),
    "ARCHIVE_PREFIX": ("", str),
    "CATEGORY_ENABLED": (True, bool),
    "CATEGORY_PREFIX": ("category", str),
    "AUTHOR_ENABLED": (True, bool),
    "AUTHOR_PREFIX": ("author", str),
    "RSS_ENABLED": (True, bool),
    "RSS_PATH": ("rss", str),
    "MICROFORMATS_ENABLED": (True, bool),
}
