"""Settings file for DJ Press."""

# DJPress settings
DJPRESS_SETTINGS = {
    "ARCHIVE_ENABLED": (True, bool),
    "ARCHIVE_PREFIX": ("", str),
    "AUTHOR_ENABLED": (True, bool),
    "AUTHOR_PREFIX": ("author", str),
    "CACHE_CATEGORIES": (True, bool),
    "CACHE_RECENT_PUBLISHED_POSTS": (False, bool),
    "CATEGORY_ENABLED": (True, bool),
    "CATEGORY_PREFIX": ("category", str),
    "MARKDOWN_EXTENSION_CONFIGS": ({}, dict),
    "MARKDOWN_EXTENSIONS": ([], list),
    "MARKDOWN_RENDERER": ("djpress.markdown_renderer.default_renderer", str),
    "MICROFORMATS_ENABLED": (True, bool),
    "PLUGINS": ([], list),
    "PLUGIN_SETTINGS": ({}, dict),
    "POST_PREFIX": ("{{ year }}/{{ month }}/{{ day }}", str),
    "POST_READ_MORE_TEXT": ("Read more...", str),
    "RECENT_PUBLISHED_POSTS_COUNT": (20, int),
    "RSS_ENABLED": (True, bool),
    "RSS_PATH": ("rss", str),
    "SITE_DESCRIPTION": ("", str),
    "SITE_TITLE": ("My DJ Press Blog", str),
    "THEME": ("default", str),
    "TRUNCATE_TAG": ("<!--more-->", str),
}
