# Search

DJ Press includes built-in search functionality that allows users to search through your posts and pages. The search system is designed to be simple by default while still being extensible through plugins.

## Enabling Search

Search is enabled by default. To disable it, set `SEARCH_ENABLED` to `False` in your settings:

```python
DJPRESS_SETTINGS = {
    "SEARCH_ENABLED": False,
}
```

## Configuration

Search can be configured using these settings:

| Setting                   | Type | Default    | Description                                  |
|---------------------------|------|------------|----------------------------------------------|
| `SEARCH_ENABLED`          | bool | `True`     | Enable/disable search functionality.         |
| `SEARCH_PREFIX`           | str  | `"search"` | Path for the search page.                    |
| `SEARCH_QUERY_MIN_LENGTH` | int  | `3`        | Minimum character length for search queries. |
| `SEARCH_QUERY_MAX_LENGTH` | int  | `100`      | Maximum character length for search queries. |

### Example Configuration

```python
DJPRESS_SETTINGS = {
    "SEARCH_ENABLED": True,
    "SEARCH_PREFIX": "find",  # Search will be at /find/
    "SEARCH_QUERY_MIN_LENGTH": 2,
    "SEARCH_QUERY_MAX_LENGTH": 200,
}
```

## Using Search in Templates

DJ Press provides several template tags to add search functionality to your theme.

### Basic Search Form

The simplest way to add search is using the `{% search_form %}` tag:

```django
{% load djpress_tags %}

<header>
  <h1>{% site_title_link %}</h1>
  {% search_form %}
</header>
```

This will render a complete search form with default styling.

### Custom Search Form

For more control over the appearance, customize the search form parameters:

```django
{% search_form placeholder="Search posts..." button_text="Go" form_class="navbar-search" input_class="form-control" button_class="btn btn-primary" %}
```

### Building Your Own Form

If you need complete control over the HTML structure, use the `{% search_url %}` tag:

```django
<form action="{% search_url %}" method="get" class="my-custom-form">
  <div class="search-wrapper">
    <input type="search" name="q" value="{{ search_query }}" placeholder="What are you looking for?">
    <button type="submit">
      <svg><!-- search icon --></svg>
    </button>
  </div>
</form>
```

## Search Results Template

Create a custom search results template by adding `search.html` to your theme:

```django
{% extends "djpress/mytheme/base.html" %}
{% load djpress_tags %}

{% block main %}
  <h1>Search Results</h1>

  {# Display the search query #}
  {% search_title outer="h2" pre_text="Results for '" post_text="'" %}

  {# Display any validation errors #}
  {% search_errors %}

  {# Show appropriate message based on state #}
  {% if search_errors %}
    {# Errors are displayed above #}
  {% elif not search_query %}
    <p>Enter a search term to find posts.</p>
  {% else %}
    {# Display search results #}
    {% for post in posts %}
      {% post_wrap %}
        {% post_title outer_tag="h3" %}
        {% post_content outer_tag="section" %}
        <footer>
          <p>By: {% post_author %} on {% post_date %}</p>
        </footer>
      {% end_post_wrap %}
    {% empty %}
      <p>No search results found for "{{ search_query }}".</p>
    {% endfor %}

    {# Pagination for search results #}
    {% pagination_links %}
  {% endif %}
{% endblock %}
```

If no `search.html` template exists, DJ Press will fall back to using `index.html`.

## Default Search Behavior

The built-in search performs a simple case-insensitive search across:

- Post titles
- Post content

Results are weighted and sorted by:

1. **Score**: Posts with matches in the title are ranked higher than content-only matches
2. **Post type**: Pages are prioritized over posts
3. **Date**: More recently updated posts appear first

### Search Implementation

The default search uses basic database queries that work across all database backends (SQLite, PostgreSQL, MySQL, etc.). For each search term:

- Title matches receive a weight of 2
- Content matches receive a weight of 1
- Posts are scored and filtered based on these weights

## Custom Search with Plugins

For more advanced search capabilities (full-text search, fuzzy matching, search indexes, etc.), you can override the default search using a plugin.

### Creating a Search Plugin

```python
from djpress.plugins import DJPressPlugin
from djpress.plugins.hook_registry import SEARCH_CONTENT
from djpress.models import Post

class Plugin(DJPressPlugin):
    name = "my_custom_search"
    hooks = [
        (SEARCH_CONTENT, "custom_search"),
    ]

    def custom_search(self, query: str):
        """Provide custom search functionality.

        Args:
            query: The search query string

        Returns:
            QuerySet of Post objects, or None to fall back to default search
        """
        try:
            if not query:
                return Post.objects.none()

            # Example: PostgreSQL full-text search
            from django.contrib.postgres.search import SearchVector

            return Post.objects.annotate(
                search=SearchVector('title', 'content'),
            ).filter(search=query)

        except Exception as e:
            import logging
            logging.error(f"Search plugin error: {e}")
            # Return None to fall back to default search
            return None
```

### Integration with External Search Services

You can also integrate with external search services like Elasticsearch, Algolia, or Meilisearch:

```python
def custom_search(self, query: str):
    """Search using Elasticsearch."""
    try:
        if not query:
            return Post.objects.none()

        # Query your search service
        results = self._query_elasticsearch(query)

        # Return matching Post objects
        post_ids = [result['id'] for result in results]
        return Post.objects.filter(id__in=post_ids)

    except Exception as e:
        import logging
        logging.error(f"Elasticsearch search error: {e}")
        return None  # Fall back to default search
```

## Validation

Search queries are validated before processing:

- **Minimum length**: Queries shorter than `SEARCH_QUERY_MIN_LENGTH` (default 2) will trigger an error.
- **Maximum length**: Queries longer than `SEARCH_QUERY_MAX_LENGTH` (default 100) will trigger an error.
- **Whitespace**: Leading and trailing whitespace is automatically stripped.

Validation errors are automatically displayed using the `{% search_errors %}` template tag.

## URL Structure

By default, search is accessible at `/search/` with the query parameter `q`:

```
https://example.com/search/?q=django
```

You can customize the search path using the `SEARCH_PREFIX` setting:

```python
DJPRESS_SETTINGS = {
    "SEARCH_PREFIX": "find",  # Search at /find/?q=django
}
```

## Security Considerations

- All search queries are automatically escaped to prevent XSS attacks
- Query length is validated to prevent abuse
- Search uses Django's ORM, protecting against SQL injection
- No user input is executed as code

## Disabling Search

To completely disable search functionality:

```python
DJPRESS_SETTINGS = {
    "SEARCH_ENABLED": False,
}
```

When disabled:

- The search URL returns a 404 error
- Search template tags return empty strings
- No database queries are performed
