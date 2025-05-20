# Configuration

## DJ Press Settings

In your `settings.py` file, create a `DJPRESS_SETTINGS` dictionary to configure your blog. Here's a basic example:

```python
# DJPress settings
DJPRESS_SETTINGS = {
    "SITE_TITLE": "My Awesome Blog",
    "POST_PREFIX": "{{ year }}/{{ month }}",
}
```

### Available Settings

Settings are grouped by functionality:

#### URL Structure

| Setting            | Type | Default                              | Description                                       |
|--------------------|------|--------------------------------------|---------------------------------------------------|
| `POST_PREFIX`      | str  | `"{{ year }}/{{ month }}/{{ day }}"` | Defines URL structure for posts. Use placeholders like `{{ year }}`, `{{ month }}`, and `{{ day }}`. |
| `ARCHIVE_ENABLED`  | bool | `True`                               | Enable/disable date-based archives.               |
| `ARCHIVE_PREFIX`   | str  | `""`                                 | Prefix for archive URLs.                          |
| `CATEGORY_ENABLED` | bool | `True`                               | Enable/disable category pages.                    |
| `CATEGORY_PREFIX`  | str  | `"category"`                         | Prefix for category URLs.                         |
| `TAG_ENABLED`      | bool | `True`                               | Enable/disable tag pages.                         |
| `TAG_PREFIX`       | str  | `"tag"`                              | Prefix for tag URLs.                              |
| `AUTHOR_ENABLED`   | bool | `True`                               | Enable/disable author pages.                      |
| `AUTHOR_PREFIX`    | str  | `"author"`                           | Prefix for author URLs.                           |
| `RSS_ENABLED`      | bool | `True`                               | Enable/disable RSS feed.                          |
| `RSS_PATH`         | str  | `"rss"`                              | Path for RSS feed.                                |

#### Content Display

| Setting                        | Type | Default              | Description                                        |
|--------------------------------|------|----------------------|----------------------------------------------------|
| `SITE_TITLE`                   | str  | `"My DJ Press Blog"` | Website title used in templates.                   |
| `SITE_DESCRIPTION`             | str  | `""`                 | Website description for metadata.                  |
| `RECENT_PUBLISHED_POSTS_COUNT` | int  | `20`                 | Number of posts displayed per page.                |
| `POST_READ_MORE_TEXT`          | str  | `"Read more..."`     | Text for "Read more" links.                        |
| `TRUNCATE_TAG`                 | str  | `"<!--more-->"`      | HTML comment that marks where to truncate content. |
| `MICROFORMATS_ENABLED`         | bool | `True`               | Enable/disable microformats in HTML.               |

#### Media Settings

| Setting             | Type | Default                                      | Description                        |
|---------------------|------|----------------------------------------------|------------------------------------|
| `MEDIA_UPLOAD_PATH` | str  | `"djpress/{{ year }}/{{ month }}/{{ day }}"` | Path pattern for uploaded files.   |

#### Markdown Configuration

| Setting                     | Type | Default                                        | Description                                    |
|-----------------------------|------|------------------------------------------------|------------------------------------------------|
| `MARKDOWN_EXTENSIONS`       | list | `[]`                                           | List of Python-Markdown extensions to enable.  |
| `MARKDOWN_EXTENSION_CONFIGS`| dict | `{}`                                           | Configuration options for markdown extensions. |
| `MARKDOWN_RENDERER`         | str  | `"djpress.markdown_renderer.default_renderer"` | Path to markdown renderer function.            |

#### Caching

| Setting                       | Type | Default | Description                                           |
|-------------------------------|------|---------|-------------------------------------------------------|
| `CACHE_CATEGORIES`            | bool | `True`  | Enable/disable caching for categories.                |
| `CACHE_TAGS`                  | bool | `False` | Enable/disable caching for tags.                      |
| `CACHE_RECENT_PUBLISHED_POSTS`| bool | `False` | Enable/disable caching for recent posts.              |
| `MAX_TAGS_PER_QUERY`          | int  | `5`     | Maximum number of tags to query for auto-suggestions. |

#### Plugin System

| Setting           | Type | Default | Description                            |
|-------------------|------|---------|----------------------------------------|
| `PLUGINS`         | list | `[]`    | List of plugin module paths to enable. |
| `PLUGIN_SETTINGS` | dict | `{}`    | Configuration options for plugins.     |

### Example Configurations

#### Minimal Blog

```python
DJPRESS_SETTINGS = {
    "SITE_TITLE": "My Personal Blog",
    "POST_PREFIX": "{{ year }}/{{ month }}",
    "THEME": "default",
}
```

#### News Site with Categories

```python
DJPRESS_SETTINGS = {
    "SITE_TITLE": "Daily News",
    "POST_PREFIX": "news",
    "CATEGORY_PREFIX": "section",
    "RECENT_PUBLISHED_POSTS_COUNT": 10,
    "THEME": "simple",
}
```

#### Technical Documentation Site

```python
DJPRESS_SETTINGS = {
    "SITE_TITLE": "Tech Docs",
    "POST_PREFIX": "articles",
    "MARKDOWN_EXTENSIONS": ["codehilite", "fenced_code", "tables"],
    "MARKDOWN_EXTENSION_CONFIGS": {
        "codehilite": {"css_class": "highlight", "linenums": True}
    },
    "CACHE_RECENT_PUBLISHED_POSTS": True,
}
```

## Themes

There are two themes included with DJ Press: "default" and "simple". They can be configured as follows:

```python
# DJPress settings
DJPRESS_SETTINGS = {
    "THEME": "simple",
}
```

To create your own theme, please read the [Theme documentation](themes.md)
