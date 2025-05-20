# Categories

Categories in DJ Press provide a primary way to organise your blog posts into topic-based sections. Unlike tags,
categories are typically hierarchical and represent broad topics.

## Creating Categories

Categories can be created in the Django admin interface. Each category has:

- **Title**: The display name of the category
- **Slug**: The URL-friendly version of the title
- **Description**: Optional text explaining what the category contains
- **Menu Order**: Controls the display order in menus and category lists

## Assigning Categories to Posts

A post can be assigned to one or more categories:

1. From the post editor in the admin interface
2. Using the category selection widget
3. Programmatically via the API

## Displaying Categories

Categories can be displayed in your templates using the template tags:

```django
{% load djpress_tags %}

{# Get all categories as a queryset #}
{% get_categories as categories %}

{# Display categories as an HTML list #}
{% blog_categories %}

{# Display categories with custom HTML #}
{% blog_categories outer_tag="div" outer_class="categories" link_class="category-link" %}
```

See [Template Tags](templatetags.md#blog_categories) for more details on category display options.

## Category URLs and Views

Each category has its own dedicated URL and view that displays all posts belonging to that category:

```text
/category/technology/
/category/software/
/category/web-development/
```

## Category Settings

Several settings affect how categories behave in your blog:

```python
DJPRESS_SETTINGS = {
    "CATEGORY_ENABLED": True,          # Enable/disable category functionality
    "CATEGORY_IN_URL": True,           # Include category in post URLs
    "CATEGORY_BASE": "category",       # Base URL path for categories
    "CACHE_CATEGORIES": True,          # Enable category caching
}
```

See [Configuration](configuration.md) for more details on these settings.

## Related Topics

- [URL Structure](url_structure.md) - How category URLs are structured
- [Template Tags](templatetags.md) - Tags for displaying categories
- [Configuration](configuration.md) - Category-related settings
