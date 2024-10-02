"""Settings file for DJ Press."""

# DJPress settings
TRUNCATE_TAG = "<!--more-->"
CACHE_CATEGORIES: bool = True
CACHE_RECENT_PUBLISHED_POSTS: bool = False
RECENT_PUBLISHED_POSTS_COUNT: int = 20
MARKDOWN_EXTENSIONS: list = []
MARKDOWN_EXTENSION_CONFIGS: dict = {}
BLOG_TITLE: str = "My DJ Press Blog"
BLOG_DESCRIPTION: str = ""
POST_READ_MORE_TEXT: str = "Read more..."

# DJPress URL settings
POST_PREFIX: str = "{{ year }}/{{ month }}/{{ day }}"
ARCHIVE_ENABLED: bool = True
ARCHIVE_PREFIX: str = ""
CATEGORY_ENABLED: bool = True
CATEGORY_PREFIX: str = "category"
AUTHOR_ENABLED: bool = True
AUTHOR_PREFIX: str = "author"
RSS_ENABLED: bool = True
RSS_PATH: str = "rss"
