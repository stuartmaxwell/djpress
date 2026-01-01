# Themes

A DJ Press theme is a collection of Django template files and static assets that control the look and feel of your blog.
This guide explains how to use existing themes, customise them, or create your own theme from scratch.

## Theme Structure

### Template Files

Template files must be placed in: `./templates/djpress/{{ your_theme_name }}/`

At minimum, a theme needs an `index.html` template. If this is the only template you provide, it will be used for all
views. For more specialised layouts, you can create these additional templates:

| Template Name   | Used For            | Example URL                                |
|-----------------|---------------------|--------------------------------------------|
| `home.html`     | Home page           | `https://yourblog.com/`                    |
| `single.html`   | Individual posts    | `https://yourblog.com/2024/05/20/my-post/` |
| `page.html`     | Static pages        | `https://yourblog.com/about/`              |
| `archives.html` | Date-based archives | `https://yourblog.com/2024/`               |
| `category.html` | Category pages      | `https://yourblog.com/category/news/`      |
| `tag.html`      | Tag pages           | `https://yourblog.com/tag/python/`         |
| `author.html`   | Author pages        | `https://yourblog.com/author/sam/`         |

When a specific template isn't available, DJ Press falls back to `index.html`.

### Static Files

Static files (CSS, JavaScript, images) should be placed in: `./static/djpress/{{ your_theme_name }}/`

Recommended organisation:

- `./static/djpress/{{ your_theme_name }}/css/`
- `./static/djpress/{{ your_theme_name }}/js/`
- `./static/djpress/{{ your_theme_name }}/img/`

Access static files in your templates using the Django `static` tag:

```django
{% load static %}
<link rel="stylesheet" href="{% static 'djpress/mytheme/css/style.css' %}">
<script src="{% static 'djpress/mytheme/js/main.js' %}"></script>
<img src="{% static 'djpress/mytheme/img/logo.png' %}" alt="Logo">
```

## Activating a Theme

To use a theme, set the `THEME` setting in your Django project's settings:

```python
DJPRESS_SETTINGS = {
    "THEME": "mytheme",
}
```

The theme name must match the directory name under `templates/djpress/` and `static/djpress/`.

## Creating a Custom Theme

Creating a custom theme involves these steps:

1. Create the necessary directories:

   ```bash
   mkdir -p templates/djpress/mytheme
   mkdir -p static/djpress/mytheme/css
   mkdir -p static/djpress/mytheme/js
   mkdir -p static/djpress/mytheme/img
   ```

2. Create an `index.html` template (minimum requirement):

   ```django
   {% load static %}
   {% load djpress_tags %}

   <!DOCTYPE html>
   <html lang="en">
   <head>
       <meta charset="UTF-8">
       <meta name="viewport" content="width=device-width, initial-scale=1.0">
       <title>{% page_title post_text="| " %}{% site_title %}</title>
       <link rel="stylesheet" href="{% static 'djpress/mytheme/css/style.css' %}">
       {% rss_link %}
   </head>
   <body>
       <header>
           <h1>{% site_title_link %}</h1>
           <nav>{% site_pages %}</nav>
       </header>

       <main>
           {% if post %}
               {% post_wrap %}
                   <h1>{% get_post_title %}</h1>
                   <div class="meta">
                       By {% post_author %} | {% post_date %}
                   </div>
                   <div class="content">
                       {% post_content %}
                   </div>
                   <div class="taxonomy">
                       Categories: {% post_categories %}
                       Tags: {% post_tags %}
                   </div>
               {% end_post_wrap %}
           {% else %}
               <h1>Latest Posts</h1>
               {% for post in posts %}
                   {% post_wrap %}
                       <h2>{% post_title %}</h2>
                       <div class="meta">
                           By {% post_author %} | {% post_date %}
                       </div>
                       <div class="content">
                           {% post_content %}
                       </div>
                   {% end_post_wrap %}
               {% empty %}
                   <p>No posts found.</p>
               {% endfor %}

               {% pagination_links %}
           {% endif %}
       </main>

       <aside>
           <h3>Categories</h3>
           {% site_categories %}

           <h3>Tags</h3>
           {% site_tags %}

           <h3>Archives</h3>
           <!-- Custom archive links could go here -->
       </aside>

       <footer>
           <p>&copy; {% now "Y" %} | Powered by DJ Press</p>
       </footer>
   </body>
   </html>
   ```

3. Create a basic CSS file (`static/djpress/mytheme/css/style.css`):

   ```css
   /* Basic styling for the theme */
   body {
       font-family: system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
       line-height: 1.6;
       margin: 0;
       padding: 0;
       display: grid;
       grid-template-columns: 1fr 300px;
       grid-template-areas:
           "header header"
           "main sidebar"
           "footer footer";
       gap: 20px;
       max-width: 1200px;
       margin: 0 auto;
       padding: 20px;
   }

   header {
       grid-area: header;
       border-bottom: 1px solid #eee;
       padding-bottom: 20px;
       margin-bottom: 20px;
   }

   main {
       grid-area: main;
   }

   aside {
       grid-area: sidebar;
       background: #f7f7f7;
       padding: 20px;
       border-radius: 5px;
   }

   footer {
       grid-area: footer;
       border-top: 1px solid #eee;
       padding-top: 20px;
       margin-top: 20px;
       text-align: center;
   }

   article {
       margin-bottom: 30px;
       padding-bottom: 20px;
       border-bottom: 1px solid #eee;
   }

   h1, h2, h3 {
       color: #333;
   }

   a {
       color: #0066cc;
       text-decoration: none;
   }

   a:hover {
       text-decoration: underline;
   }

   .meta {
       color: #666;
       font-size: 0.9em;
       margin-bottom: 15px;
   }

   .taxonomy {
       font-size: 0.9em;
       margin-top: 15px;
   }
   ```

4. Activate your theme in settings:

   ```python
   DJPRESS_SETTINGS = {
       "THEME": "mytheme",
   }
   ```

## Template Context

DJ Press provides these context variables to your templates:

| Context Variable | Type                | Available In           | Description                              |
|------------------|---------------------|------------------------|------------------------------------------|
| `post`           | Post object         | Single post/page views | The current post or page                 |
| `posts`          | Paginator Page      | Index views            | Collection of posts for the current page |
| `category`       | Category object     | Category views         | The current category                     |
| `author`         | User object         | Author views           | The current author                       |
| `tags`           | List of Tag objects | Tag views              | The current tag(s)                       |

## Conditional Template Logic

You can use conditional logic to create different layouts based on the view type:

```django
{% if post %}
    {# Single post/page view #}
    <h1>{{ post.title }}</h1>
{% elif category %}
    {# Category view #}
    <h1>Category: {{ category.title }}</h1>
{% elif author %}
    {# Author view #}
    <h1>Posts by {{ author.get_full_name }}</h1>
{% else %}
    {# Home or archive view #}
    <h1>Blog Posts</h1>
{% endif %}
```

## Built-in Themes

DJ Press includes two reference themes:

1. **default** - A minimalist theme with a single `index.html` template
2. **simple** - A basic theme that demonstrates using different template types

You can use these as starting points for your own themes.

## Recommended Workflow

1. Start by copying one of the built-in themes
2. Modify templates and styles to match your design
3. Test with different content types (posts, pages, archives)
4. Optimise for mobile devices with responsive CSS

## Advanced Theme Techniques

### Template Inheritance

For more maintainable themes, use Django's template inheritance:

```django
{# base.html #}
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}{% site_title %}{% endblock %}</title>
    {% block head %}{% endblock %}
</head>
<body>
    <header>{% block header %}{% endblock %}</header>
    <main>{% block content %}{% endblock %}</main>
    <footer>{% block footer %}{% endblock %}</footer>
</body>
</html>
```

```django
{# single.html #}
{% extends "djpress/mytheme/base.html" %}

{% block title %}{{ post.title }} | {% site_title %}{% endblock %}

{% block content %}
    <article>{{ post.content_markdown }}</article>
{% endblock %}
```

### Custom Filters

You can create custom template filters for your theme by creating a `templatetags` directory in your app. But if there
are missing tags, then it would help us to raise an [issue on GitHub](https://github.com/stuartmaxwell/djpress/issues)
so we can consider adding them in DJ Press core.
