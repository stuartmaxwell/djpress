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
| `AUTHOR_ENABLED`   | bool | `False`                              | Enable/disable author pages.                      |
| `AUTHOR_PREFIX`    | str  | `"author"`                           | Prefix for author URLs.                           |
| `RSS_ENABLED`      | bool | `True`                               | Enable/disable RSS feed.                          |
| `RSS_PATH`         | str  | `"rss"`                              | Path for RSS feed.                                |
| `SEARCH_ENABLED`   | bool | `True`                               | Enable/disable search functionality.              |
| `SEARCH_PREFIX`    | str  | `"search"`                           | Path for search page.                             |

#### Content Display

| Setting                        | Type | Default              | Description                                         |
|--------------------------------|------|----------------------|-----------------------------------------------------|
| `SITE_TITLE`                   | str  | `"My DJ Press Blog"` | Website title used in templates.                    |
| `SITE_DESCRIPTION`             | str  | `""`                 | Website description for metadata.                   |
| `RECENT_PUBLISHED_POSTS_COUNT` | int  | `20`                 | Number of posts displayed per page.                 |
| `POST_READ_MORE_TEXT`          | str  | `"Read more..."`     | Text for "Read more" links.                         |
| `TRUNCATE_TAG`                 | str  | `"<!--more-->"`      | HTML comment that marks where to truncate content.  |
| `MICROFORMATS_ENABLED`         | bool | `True`               | Enable/disable microformats in HTML.                |
| `SEARCH_QUERY_MIN_LENGTH`      | int  | `2`                  | Minimum character length for search queries.        |
| `SEARCH_QUERY_MAX_LENGTH`      | int  | `100`                | Maximum character length for search queries.        |
| `MAX_TAGS_PER_QUERY`           | int  | `5`                  | Maximum number of tags that can be queried at once. |

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

#### Plugin System

| Setting           | Type | Default | Description                            |
|-------------------|------|---------|----------------------------------------|
| `PLUGINS`         | list | `[]`    | List of plugin module paths to enable. |
| `PLUGIN_SETTINGS` | dict | `{}`    | Configuration options for plugins.     |

#### Theme Settings

| Setting          | Type | Default   | Description                                                                     |
|------------------|------|-----------|---------------------------------------------------------------------------------|
| `THEME`          | str  | `default` | Which theme to use. See the [themes](themes.md) page for more details.          |
| `THEME_SETTINGS` | dict | `{}`      | Optional theme settings. Refer to the specific theme documentation for details. |

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

## Custom User Models

If your Django project uses a custom user model (`AUTH_USER_MODEL`), you should consider how author display names and
archive pages are generated.

### Author Display Names

The author's name is rendered in templates using the `{% post_author %}` tag. DJ Press resolves the author's display
name in the following order of preference:

1. **`get_full_name()`**: If your custom user model implements a custom `get_full_name()` method, it will be used first.
2. **`first_name` & `last_name`**: If the user model has direct `first_name` and `last_name` fields, it will concatenate them.
3. **`get_username()`**: Falls back to the username field defined by your custom user model.

**Note**: If your custom user model uses the email address as the unique username (login identifier) and does not
define a `first_name`/`last_name` or implement a custom `get_full_name()` method, the user's plain email address will
be rendered as their display name on the public website. To prevent this, ensure that your custom user model implements
a custom `get_full_name()` method returning a safe display name.

### Author Archive URLs

By default, author archive URLs are disabled (`AUTHOR_ENABLED = False`). If you choose to enable them by setting
`"AUTHOR_ENABLED": True` in your `DJPRESS_SETTINGS`:

- The URL slug generated for an author relies on the string returned by `get_username()`.
- Ensure that `get_username()` returns a URL-safe string consisting only of letters, numbers, underscores, and hyphens (matching the pattern `^[\w-]+$`).
- If `get_username()` returns an email address or a string containing spaces, dots, or special characters, those characters will violate the URL routing regular expression pattern and will cause 404 page-not-found errors when visitors try to view the author's archive.

## Dynamic Database Settings

For most simple use-cases, configuring settings in the `DJPRESS_SETTINGS` object is recommended. However, DJ Press
allows you to configure settings in your database via a `Setting` model, which takes precedence over the file-based
settings and defaults.

This allows administrators to change settings like `SITE_TITLE` or `SITE_DESCRIPTION` directly from the Django Admin interface without needing to redeploy or modify code files.

### Enabling Dynamic Database Settings

Dynamic database settings are disabled by default. To enable them, add the `DATABASE_SETTINGS_ENABLED` toggle to your
`DJPRESS_SETTINGS` dictionary in your `settings.py` file:

```python
DJPRESS_SETTINGS = {
    "DATABASE_SETTINGS_ENABLED": True,
}
```

### Database Settings Precedence

When `DATABASE_SETTINGS_ENABLED` is `True`, settings are resolved in the following order of precedence:

1. **Database settings** (configured via the `Setting` model in Django Admin).
2. **Django settings** (defined in `DJPRESS_SETTINGS` inside `settings.py`).
3. **App defaults** (pre-defined defaults in `app_settings.py`).

If a setting key does not exist in the database, DJ Press falls back to the subsequent layers. Unrecognised
keys in the database are safely ignored.

### Caching and Performance

To avoid executing a database query on every setting retrieval, DJ Press utilises Django's default caching framework.

All database settings are retrieved in a single query and cached globally under the key `"djpress:settings"`. In addition, to prevent redundant cache backend calls (network roundtrips), settings are cached in-memory for the lifetime of each HTTP request. The cache is automatically invalidated and refreshed whenever a setting is created, saved, or deleted.

> [!IMPORTANT]
> **Multi-Process Environments & Cache Requirements**
> If your site runs on a multi-process server (such as multiple Gunicorn/uWSGI workers, or multiple containers) and you enable dynamic database settings, you **must** configure a shared caching backend (like **Redis**, **Memcached**, or Django's built-in **Database Cache**).
>
> If you do not configure a shared cache, Django will fall back to using `LocMemCache` (local memory cache). Because `LocMemCache` is isolated to the memory of each individual worker process, setting updates made on one worker process will not propagate to the other processes until they are restarted.


### Configuring Settings in Django Admin

When configuring settings via the Django Admin interface:
- **Keys**: Enter any setting key (e.g. `SITE_TITLE`, `RSS_ENABLED`, `RECENT_PUBLISHED_POSTS_COUNT`).
- **Values**: Stored as a standard JSONField. To make this easier, the admin form uses a custom parser:
  - **Booleans**: Enter standard Python/JSON booleans (`True` / `true` / `False` / `false`) directly without quotes.
  - **Null values**: Enter `None` or `null` directly.
  - **Text strings**: Plain text strings (e.g. `My Awesome Blog`) can be entered **without quotes**. The form field will automatically fall back to raw strings if standard JSON parsing fails.
  - **Numbers and Collections**: Standard numbers (e.g. `10`) or JSON collections (e.g. `["markdown.extensions.tables"]` or `{"theme_color": "blue"}`) are parsed natively into their correct types.
- **Validation**: Any setting matching a key in `DJPRESS_SETTINGS` is validated when saved to ensure that the value's type matches the expected setting type, preventing configuration mistakes.
- **Lockout Protection**: To avoid circular conflicts, the system-level master toggle `DATABASE_SETTINGS_ENABLED` cannot be configured in the database and must be configured in the file-based settings.
