# Template Tags

DJ Press provides a rich set of template tags to help you build your blog templates. These tags allow you to retrieve
and display data from your blog, create navigation menus, format dates, and more.

## Loading Template Tags

To use any of the following tags, you must load the `djpress_tags` in your template file:

```django
{% load djpress_tags %}
```

## Tag Categories

The template tags in DJ Press are organised into several functional categories:

1. **Data Access Tags** - Tags that start with `get_` retrieve data from the database without any HTML formatting
2. **Display Tags** - Format and display data with appropriate HTML (e.g., `site_title_link`, `site_categories`)
3. **Post Content Tags** - Handle rendering post content, titles, dates, etc. (e.g., `post_title`, `post_content`)
4. **Navigation Tags** - Generate navigation elements like menus (e.g., `site_pages_list`, `site_categories`)
5. **Utility Tags** - Additional helper tags for common operations

## Table of Contents

- [Data Access Tags](#data-access-tags)
- [Display Tags](#display-tags)
- [Navigation Tags](#navigation-tags)
- [Post Content Tags](#post-content-tags)
- [Search Tags](#search-tags)
- [Utility Tags](#utility-tags)

## Data Access Tags

These tags retrieve data from your blog without adding any HTML formatting. They're useful when you want to access data
but apply your own custom formatting. These tags all start with `get_`.

### get_site_title

Returns the title of the site as configured in the DJ Press setting `SITE_TITLE`.

**Returns:** string containing the site title.

#### get_site_title Example

```django
<h1>{% get_site_title %}</h1>
```

### get_site_description

Returns the description of the site as configured in the DJ Press setting `SITE_DESCRIPTION`.

**Returns:** string containing the site description.

#### get_site_description Example

```django
<h1>{% get_site_description %}</h1>
```

### get_theme_setting

This is used to retrieve a theme-specific setting that a theme author has configured in their theme.
Theme settings are added to the `DJPRESS_SETTINGS` dict in the `THEME_SETTINGS` key with the specific theme as a key.
When retrieving the setting, a default value can be provided if the setting has not been configured.

#### get_theme_setting Parameters

- name (str): The name of the setting to retrieve.
- default (str|int|float|None): The default value to return if the setting is not found. If not provided, `None` will
  be returned.

**Returns:** The value as configured in the settings, or the default value if not found, or `None` if not found and no
default is provided.

#### get_theme_setting Example

For example, for a theme called `my_theme`, the setting `avatar_url` would be configured as follows:

```python
DJPRESS_SETTINGS = {
    "THEME_SETTINGS": {
        "my_theme": {
            "avatar_url": "https://example.com/avatar.jpg",
        }
    }
}
```

And then the setting can be retrieved from the theme using:
`{% get_theme_setting "avatar_url" "https://api.dicebear.com/9.x/bottts/svg" %}`
This would return the avatar url as configured in the settings, or if not provided, would fall back to the default
value (using the excellent [DiceBear](https://www.dicebear.com/) service as an example.)

Another example for how this can be used, is to leave out the default value, and then check for this in the theme code.

```django
{% get_theme_setting "avatar_url" as avatar_url %}
{% if avatar_url %}
<img src="{{ avatar_url }}" alt="Avatar">
{% endif %}
```

### get_posts

Returns all published posts as a queryset. Use this tag to access all published blog posts in your templates.

**Returns:** queryset of all published posts.

**Related Topics:** See [url_structure.md](url_structure.md) for URL patterns and [themes.md](themes.md) for how to
use posts in your theme.

#### get_posts Example

This is useful for building an index page with all posts:

```django
{% get_posts as all_posts %}

{% for post in all_posts %}
<ul>
  <li>{{ post.title }}</li>
</ul>
{% endfor %}
```

### get_recent_posts

Returns the most recent published posts as a queryset. Tries to be efficient by checking if there's a `posts` object in
the context that can be used.

**Returns:** queryset of recent published posts.

#### get_recent_posts Example

```django
{% get_recent_posts as recent_posts %}

<h3>Recent Posts</h3>
<ul>
  {% for post in recent_posts %}
  <li><a href="{{ post.url }}">{{ post.title }}</a></li>
  {% endfor %}
</ul>
```

### get_pages

Returns all published pages as a queryset. This can be useful if you want to build your own menu or list of pages
on the blog.

**Returns:** queryset of published pages that are sorted by the `menu_order` field, and then by the `title` field.

#### get_pages Example

Get the pages and display as a list:

```django
{% get_pages as pages %}
<ul>
  {% for page in pages %}
    <li>
      <a href="{% url 'djpress:single_post' page.slug %}">{{ page.title }}</a>
    </li>
  {% endfor %}
</ul>
```

Outputs the following:

```html
<ul>
  <li>
    <a href="/about/">About me</a>
  </li>
  <li>
    <a href="/contact/">Contact me</a>
  </li>
</ul>
```

**Related Topics:** See [`site_pages`](#site_pages) for a tag that produces similar output to the above but with just a
single template tag.

### get_categories

Get all categories as an iterable queryset. This can be useful if you want to build your own menu or list of categories
on the blog.

**Returns:** queryset of categories that are sorted by the `menu_order` field, and then by the `title` field.

**Related Topics:** Also see `site_categories` for a tag that produces similar output to the below example, but with
just a single template tag.

#### get_categories Example

Get the categories and display as a list:

```django
{% get_categories as categories %}
<ul>
  {% for category in categories %}
    <li>
      <a href="{% url 'djpress:category_posts' category.slug %}">{{ category.title }}</a>
    </li>
  {% endfor %}
</ul>
```

Outputs the following:

```html
<ul>
  <li>
    <a href="/category/general/">General</a>
  </li>
  <li>
    <a href="/category/news/">News</a>
  </li>
</ul>
```

### get_tags

Returns all tags as a queryset.

**Returns:** queryset of all tags.

**Related Topics:** Also see `site_tags` for a template tag that produces similar output to the below example, but with
just a single template tag.

#### get_tags Example

```django
{% get_tags as all_tags %}
<div class="tag-cloud">
  {% for tag in all_tags %}
    <a href="{% url 'djpress:tag_posts' tag.slug %}" class="tag">{{ tag.title }}</a>
  {% endfor %}
</div>
```

### get_post_title

Returns the title of a post from the current context.

#### get_post_title Parameters

- `include_empty` (boolean): Whether to include the title if it is empty, using the post_title property fallback.
Default is false.

**Returns:** string - the title of the post. If there's no `post` in the context and empty string is returned.

#### get_post_title Example

```django
{% get_post_title as title %}
<meta property="og:title" content="{{ title }}">
```

### get_post_url

Returns the URL for a post from the current context.

**Returns:** string - the URL of the post. If there's no `post` in the context and empty string is returned.

#### get_post_url Example

```django
{% get_post_url as post_url %}
<meta property="og:url" content="{{ post_url }}">
```

### get_post_author

Returns the author display name from the current context.

**Returns:** string - the author display name. If there's no `post` in the context and empty string is returned.

#### get_post_author Example

```django
{% get_post_author as author %}
<meta property="article:author" content="{{ author }}">
```

### get_post_date

Returns the date of a post from the current context.

**Returns:** string - the date of the post in the format "Mon DD, YYYY". If there's no `post` in the context and empty
string is returned.

#### get_post_date Example

```django
{% get_post_date as post_date %}
<meta property="article:published_time" content="{{ post_date }}">
```

### get_post_categories

Returns a queryset of the categories that the post belongs to. Useful for building a list of categories that a post
belongs to.

**Returns:** queryset - the post's categories.

**Related Topics:** Also see `post_categories` for a template tag that returns safely marked HTML that can be used to
create a list of categories.

#### get_post_categories Example

```django
{% get_post_categories as post_categories %}
<ul>
{% for category in post_categories %}
  <li><a href="{{ category.url }}">{{ category.name }}</a></li>
{% endfor %}
</ul>
```

### get_post_category_slugs

Returns a list of the category slugs that the post belongs to. Useful for checking if a post belongs to a specific
category.

**Returns:** list - the post's category slugs.

#### get_post_category_slugs Example

```django
{% get_post_category_slugs as category_slugs %}
{% if "news" in category_slugs %}
  <p>This post is in the news category.</p>
{% endif %}
```

### get_rss_url

Returns the URL of the RSS feed if the `RSS_ENABLED` is set to True (which is the default).

**Returns:** string - the URL to the RSS feed, e.g. "http://example.com/rss".

**Related Topics:** See `rss_link` for a tag that returns the below example with a single template tag.

#### get_rss_url Example

```django
{% get_rss_url as rss_url %}
{% if rss_url %}
  <link rel="alternate" type="application/rss+xml" title="Latest Posts" href="{{ rss_url }}">
{% endif %}
```

### get_search_url

Returns the URL which is used to `POST` a search query to. This is useful for building a custom search form.
The `SEARCH_ENABLED` setting must be set to True (which is the default).

**Returns:** string - the URL to the search page, e.g. "http://example.com/search" or an empty string if
`SEARCH_ENABLED` is False.

**Related Topics:** See `search_form` for a tag that returns a pre-built search form with a single template tag.

#### get_search_url Example

```django
{% get_search_url as search_url %}
{% if search_url %}
  <form action="{{ search_url }}" method="post">
    <input type="text" name="q" placeholder="Search...">
    <button type="submit">Search</button>
  </form>
{% endif %}
```

### get_pagination_range

Returns an iterable range of numbers, starting at 1, for the range of paginated results. Useful for building a custom
pagination menu.

**Returns:** iterable - an iterable range of numbers, starting at 1, for the range of paginated results.

**Related Topics:** See `get_pagination_current_page` for a tag that returns the current page number,
and `pagination_links` for a tag that returns safely marked HTML links for the previous and next pages.

#### get_pagination_range Example

```django
{% get_pagination_range as pagination_range %}
{% if pagination_range %}
  <ul>
    {% for page in pagination_range %}
      <li><a href="?page={{ page }}">{{ page }}</a></li>
    {% endfor %}
  </ul>
{% endif %}
```

### get_pagination_current_page

Returns the current page number. Useful for building a custom pagination menu.

**Returns:** int - the current page number.

**Related Topics:** See `get_pagination_range` for a tag that returns an iterable range of page numbers,
and `pagination_links` for a tag that returns safely marked HTML links for the previous and next pages.

#### get_pagination_current_page Example

```django
{% get_pagination_range as pagination_range %}
{% get_pagination_current_page as current_page %}
{% if pagination_range %}
  <ul>
    {% for page in pagination_range %}
      {% if current_page == page %}
        <li><a href="?page={{ page }}" class="active">{{ page }}</a></li>
      {% else %}
        <li><a href="?page={{ page }}">{{ page }}</a></li>
      {% endif %}
    {% endfor %}
  </ul>
{% endif %}
```

## Display Tags

These tags retrieve data and format it with HTML, ready to be displayed in your templates.

### site_title

Returns safely-marked HTML with the site title as configured in the settings with the `SITE_TITLE` variable. If no site
title has been configured, this will return the default title: "My DJ Press Blog".

**Returns:** safely-marked HTML with the `SITE_TITLE` value as a string.

**Related Topics:** See [configuration.md](configuration.md) for how to configure the site title and other settings.

#### site_title Parameters

- `outer_tag` (str): The HTML tag to wrap the site title in. Optional - if ommitted, no outer element will be used.
- `outer_class` (str): CSS class(es) to apply to the outer element. Optional.
- `link` (bool): Whether to wrap the site title in a link. Optional, default is False.
- `link_class` (str): CSS class(es) to apply to the link. Optional.

**Note:** `outer_tag` can be passed as a positional argument, but the other parameters must be passed as keyword arguments.

#### site_title Examples

Create a header title for your site:

```django
{% site_title "h1" %}
```

or:

```django
{% site_title outer_tag="h1" %}
```

will produce:

```django
<h1>My DJ Press Blog</h1>
```

Create a header title for your site with a link:

```django
{% site_title "h1" link=True %}
```

will produce:

```django
<h1><a href="/">My DJ Press Blog</a></h1>
```

Or with all options:

```django
{% site_title outer_tag="h1" outer_class="title" link=True link_class="link" %}
```

will produce:

```django
<h1 class="title"><a href="/" class="link">My DJ Press Blog</a></h1>
```

### site_description

Returns safely-marked HTML with the site description as configured in the settings with the `SITE_DESCRIPTION`
variable. If no site description has been configured, this will return an empty string.

**Returns:** safely-marked HTML with the `SITE_DESCRIPTION` value as a string.

**Related Topics:** See [configuration.md](configuration.md) for how to configure the site description and other settings.

#### site_description Parameters

- `outer_tag` (str): The HTML tag to wrap the site description in. Optional - if ommitted, no outer element will be used.
- `outer_class` (str): CSS class(es) to apply to the outer element. Optional.

**Note:** `outer_tag` can be passed as a positional argument, but the other parameters must be passed as keyword arguments.

#### site_description Examples

Create a header description for your site:

```django
{% site_description "h2" %}
```

or:

```django
{% site_description outer_tag="h2" %}
```

will produce:

```django
<h2>My site's description.</h2>
```

Or with all options:

```django
{% site_description outer_tag="h2" outer_class="subtitle" %}
```

will produce:

```django
<h2 class="subtitle">My site's description.</h2>
```

### page_title

Returns the title of the page, depending on the context of the page. A different title is returned for a category page,
a blog page, author page, etc. This is useful to be used in the `<title>` tag of the template.

**Returns:** A string with no HTML formatting.

#### page_title Parameters

- `pre_text` (str): text to be displayed before the page title. Optional.
- `post_text` (str): text to be displayed after the page title. Optional.

#### page_title Examples

The tag with no options for a single blog page or post:

```django
<title>{% page_title %}</title>
```

Outputs the following:

```html
<title>My blog post title</title>
```

The tag can be combined with the `site_title` tag as well as using the `post_text` field.

```django
<title>{% page_title post_text=" | " %}{% site_title %}</title>
```

Outputs the following:

```html
<title>My blog post title | My DJ Press Blog</title>
```

Or you can get creative with an emoji:

```django
<title>{% page_title pre_text="🚀 " post_text=" | " %}{% site_title %}</title>
```

Outputs the following:

```html
<title>🚀 My blog post title | My DJ Press Blog</title>
```

Category pages will show the title of the category, and author pages will show the display name of the author.

### site_categories

Get a list of all categories wrapped in HTML that can be configured with optional arguments.

**Returns:** all categories as HTML which has been marked as safe.

> **Related Topics:** See [url_structure.md](url_structure.md) for category URL patterns and [configuration.md](configuration.md) for category-related settings.

#### site_categories Parameters

- `outer_tag` (str): the outer tag that this should be wrapped in. Accepted options are "ul", "div", "span". If "ul" is used, then the inner items will be wrapped with "li" tags.
Default is: "ul".
- `outer_class` (str): the CSS classes to apply to the outer tag. Default: "".
- `link_class` (str): the CSS classes to apply to the link tag. Default: "".
- `separator` (str): the separator to use between categories. Only relevant when not using "ul" as the outer tag.
Default: ", ".
- `pre_text` (str): the text to prepend to the list of categories. Only relevant when not using "ul" as the outer tag.
Default: "".
- `post_text` (str): the text to append to the list of categories. Only relevant when not using "ul" as the outer tag.
Default: "".

**Note:** `outer_tag` can be passed as a positional argument, but the other parameters must be passed as keyword arguments.

#### site_categories Examples

Just the tag, with no arguments.

```django
{% site_categories %}
```

```html
<ul>
  <li>
    <a href="/category/general/" title="View all posts in the General category">General</a>
  </li>
  <li>
    <a href="/category/news/" title="View all posts in the General category">News</a>
  </li>
</ul>
```

Wrapped in a `div` tag:

```django
{% site_categories "div" %}
```

```html
<div>
  <a href="/category/general/" title="View all posts in the General category">General</a>,
  <a href="/category/news/" title="View all posts in the General category">News</a>
</div>
```

Wrapped in a `span` tag with all optional parameters:

```django
{% site_categories "span" outer_class="class1" link_class="class2" separator=" | " pre_text="Categories: " post_text="." %}
```

```html
<span class="class1">Categories:
  <a href="/category/general/" title="View all posts in the General category" class="class2">General</a> | <a href="/category/news/" title="View all posts in the General category" class="class2">News</a>.
</span>
```

### site_tags

Get a list of all tags wrapped in HTML that can be configured with optional arguments.

**Returns:** all tags as HTML which has been marked as safe.

> **Related Topics:** See [tags.md](tags.md) for more information about tags and [url_structure.md](url_structure.md)
for tag URL patterns.

#### site_tags Parameters

- `outer_tag` (str): the outer tag that this should be wrapped in. Accepted options are "ul", "div", "span". If "ul" is used, then the inner items will be wrapped with "li" tags.
Default is: "ul".
- `outer_class` (str): the CSS classes to apply to the outer tag. Default: "".
- `link_class` (str): the CSS classes to apply to the link tag. Default: "".
- `separator` (str): the separator to use between categories. Only relevant when not using "ul" as the outer tag.
Default: ", ".
- `pre_text` (str): the text to prepend to the list of categories. Only relevant when not using "ul" as the outer tag.
Default: "".
- `post_text` (str): the text to append to the list of categories. Only relevant when not using "ul" as the outer tag.
Default: "".

**Note:** `outer_tag` can be passed as a positional argument, but the other parameters must be passed as keyword arguments.

#### site_tags Examples

Just the tags, with no arguments.

```django
{% site_tags %}
```

Outputs a list of all tags:

```html
<ul>
  <li>
    <a href="/tag/python/" title="View all posts tagged with Python">Python</a>
  </li>
  <li>
    <a href="/tag/django/" title="View all posts tagged with Django">Django</a>
  </li>
</ul>
```

Wrapped in a `div` tag:

```django
{% site_tags "div" %}
```

```html
<div>
  <a href="/tag/python/" title="View all posts tagged with Python">Python</a>,
  <a href="/tag/django/" title="View all posts tagged with Django">Django</a>
</div>
```

Wrapped in a `span` tag with all optional parameters:

```django
{% site_tags "span" outer_class="class1" link_class="class2" separator=" | " pre_text="Tags: " post_text="." %}
```

```html
<span class="class1">Tags:
<a href="/tag/python/" title="View all posts tagged with Python" class="class2">Python</a> |
<a href="/tag/django/" title="View all posts tagged with Django" class="class2">Django</a>.
</span>
```

### tags_with_counts

Get a list of all tags with post counts wrapped in HTML that can be configured with optional arguments.

**Returns:** all tags with post counts as HTML which has been marked as safe.

#### tags_with_counts Parameters

- `outer_tag` (str): the outer tags that this should be wrapped in.  Optional, default is: "ul".
- `outer_class` (str): the CSS classes to apply to the outer tag. Optional, default: "".
- `link_class` (str): the CSS classes to apply to the link tag. Optional, default: "".

**Note:** `outer_tag` can be passed as a positional argument, but the other parameters must be passed as keyword arguments.

#### tags_with_counts Examples

Just the tag, with no arguments.

```django
{% tags_with_counts %}
```

Outputs a list of all tags with post counts:

```html
<ul>
  <li>
    <a href="/tag/python/" title="View all posts tagged with Python">Python</a> (5)
  </li>
  <li>
    <a href="/tag/django/" title="View all posts tagged with Django">Django</a> (3)
  </li>
</ul>
```

Wrapped in a `div` tag with classes added.

```django
{% tags_with_counts outer_tag="div" outer_class="tag-cloud" link_class="tag" %}
```

Outputs a comma-separated list of tags with post counts, wrapped in a `div` tag.

```html
<div class="tag-cloud">
  <a href="/tag/python/" title="View all posts tagged with Python" class="tag">Python</a> (5),
  <a href="/tag/django/" title="View all posts tagged with Django" class="tag">Django</a> (3)
</div>
```

### site_pages

Get all site pages as a single-level list, wrapped in HTML that can be configured with optional arguments.

**Returns:** all blog pages as HTML marked as safe.

#### site_pages Parameters

- `outer` (str): the outer tags that this should be wrapped in. Accepted options are "ul", "div", "span".
Optional, default is: "ul".
- `outer_class` (str): the CSS classes to apply to the outer tag. Optional, default: "".
- `link_class` (str): the CSS classes to apply to the link tag. Optional, default: "".

#### site_pages Examples

Just the tag, with no arguments.

```django
{% site_pages %}
```

This will output the same HTML from the `get_pages` example.

```html
<ul>
  <li>
    <a href="/about/">About me</a>
  </li>
  <li>
    <a href="/contact/">Contact me</a>
  </li>
</ul>
```

Wrapped in a `div` tag with classes added, using positional arguments.

```django
{% site_pages "div" "class1" %}
```

Outputs a comma-separated list of pages, wrapped in a `div` tag.

```html
<div class="class1">
  <a href="/about/">About me</a>,
  <a href="/contact/">Contact me</a>
</div>
```

Wrapped in a `span` tag with classes added, using named arguments.

```django
{% site_pages outer="span" outer_class="class1" link_class="class2" %}
```

Outputs the same comma-separated list of pages, but wrapped in a `span` tag.

```html
<span class="class1">
  <a href="/about/" class="class2">About me</a>,
  <a href="/contact/" class="class2">Contact me</a>
</span>
```

### site_pages_list

Get all published site pages and output as a nested list to support parent-child page relationships. This tag is ideal
for building hierarchical navigation menus that reflect your page structure.

**Returns:** HTML which has been marked as safe.

> **Related Topics:** See [url_structure.md](url_structure.md) for page URL patterns and [themes.md](themes.md) for
> creating navigation in your theme.

#### site_pages_list Parameters

- `ul_outer_class` (str): The CSS class(es) for the outer unordered list. Optional.
- `li_class` (str): The CSS class(es) for the list item tags. Optional.
- `a_class` (str): The CSS class(es) for the anchor tags. Optional.
- `ul_child_class` (str): The CSS class(es) for the nested unordered lists. Optional.
- `include_home` (bool): Whether to include the home page in the list. Optional, default is False.
- `levels` (int): The maximum depth of the nested list. Optional, default is 0 (no limit).

#### site_pages_list Examples

Just the tag, with no arguments.

```django
{% site_pages_list %}
```

```html
<ul>
  <li>
    <a href="/about/">About me</a>
    <ul>
      <li>
        <a href="/about/hobbies/">Hobbies</a>
      </li>
      <li>
        <a href="/about/resume/">My Resume</a>
      </li>
    </ul>
  </li>
  <li>
    <a href="/contact/">Contact me</a>
  </li>
</ul>
```

With CSS classes, and extra parameters:

```django
{% site_pages_list ul_outer_class="main-nav" li_class="nav-item" a_class="nav-link" ul_child_class="sub-nav" include_home=True levels=2 %}
```

```html
<ul class="main-nav">
  <li class="nav-item">
    <a href="/" class="nav-link">Home</a>
  </li>
  <li class="nav-item">
    <a href="/about/" class="nav-link">About me</a>
    <ul class="sub-nav">
      <li class="nav-item">
        <a href="/about/hobbies/" class="nav-link">Hobbies</a>
      </li>
      <li class="nav-item">
        <a href="/about/resume/" class="nav-link">My Resume</a>
      </li>
    </ul>
  </li>
  <li class="nav-item">
    <a href="/contact/" class="nav-link">Contact me</a>
  </li>
</ul>
```

## Post Content Tags

These tags help you display the content of posts. They only work if there is a `post` object in the context.

### post_title

Display the title of a post, with intelligent handling of linking depending on the context.

- In a single post view, displays just the title with no link.
- In a posts list view, displays the title with a link to the full post.

**Returns:** HTML with the post title, marked as safe.

> **Related Topics:** See [themes.md](themes.md) for more about post display in templates and [url_structure.md](url_structure.md) for post URL patterns.

#### post_title Parameters

- `outer_tag` (str): The outer HTML tag for the title. Accepted options are "h1", "h2", "h3", "h4", "h5", "h6",
  "p", "div", "span". Optional, if not provided, no outer tag is used.
- `link_class` (str): The CSS class(es) to apply to the link if the title is linked. Optional.
- `force_link` (bool): Boolean. If true, always links the title even in a single post view. Optional, default is false.
- `include_empty` (bool): Boolean. If true, includes the title even if it is empty, using the post_title property
  fallback. Optional, default is false.

**Note:** `outer_tag` can be passed as a positional argument, but the other parameters must be passed as keyword arguments.

#### post_title Examples

Basic usage in a template:

```django
{% post_title %}
```

In a single post view, this will output:

```html
My Blog Post Title
```

In a posts list view, this will output:

```html
<a href="/2025/05/blog-post/" title="My Blog Post Title">My Blog Post Title</a>
```

With an outer tag and custom link class:

```django
{% post_title outer_tag="h1" link_class="post-title-link" %}
```

In a single post view with microformats enabled, this will output:

```html
<h1 class="p-name">My Blog Post Title</h1>
```

In a posts list view with microformats enabled, this will output:

```html
<h1 class="p-name">
  <a href="/2025/05/blog-post/" title="My Blog Post Title" class="u-url post-title-link">My Blog Post Title</a>
</h1>
```

Force link in a single post view:

```django
{% post_title force_link=True %}
```

This will always generate a link to the post, even in single post view.

### post_content

Display the content of a post with intelligent handling of both single posts and post lists.

- In a single post view, returns the full content of the post.
- In a posts list view, returns the truncated content with a "read more" link.

**Returns:** HTML content for the post which has been marked as safe.

**Related Topics:** See [themes.md](themes.md) for more about content display and
[configuration.md](configuration.md) for content truncation settings.

#### post_content Parameters

- `outer_tag` (str): The outer HTML tag to wrap the content in. Accepted options are "section", "div", "article",
  "p", "span". Optional, if not provided, no outer tag is used.
- `read_more_link_class` (str): The CSS class(es) to apply to the "read more" link. Optional.
- `read_more_text` (str): The text to use for the "read more" link. If not provided, defaults to "Read more". Optional.

**Note:** `outer_tag` can be passed as a positional argument, but the other parameters must be passed as keyword arguments.

#### post_content Examples

Basic usage in a template:

```django
{% post_content %}
```

This will output the full content of a post in a single post view, or the truncated content with a "read more" link in
a posts list view.

With custom read more text and an outer tag:

```django
{% post_content outer_tag="div" read_more_link_class="btn btn-primary" read_more_text="Continue reading..." %}
```

This will output:

```html
<!-- In a single post view -->
<div class="e-content">
  <p>This is the full content of the post...</p>
</div>

<!-- In a posts list view -->
<div class="e-content">
  <p>This is the truncated content of the post...</p>
  <a href="/2023/05/sample-post/" class="btn btn-primary">Continue reading...</a>
</div>
```

Note: The `class="e-content"` will only be added if Microformats are enabled in the configuration.

### post_date

Display the date of a post, optionally with links to the archives if archive functionality is enabled.

**Returns:** HTML with formatted date information, marked as safe.

**Related Topics:** See [url_structure.md](url_structure.md) for archive URL patterns and
[configuration.md](configuration.md) for date/archive settings.

#### post_date Parameters

- `link_class` (str): The CSS class(es) to apply to the date links. Optional.

#### post_date Examples

Basic usage in a template:

```django
{% post_date %}
```

If archive functionality is disabled, this will output:

```html
May 20, 2025
```

If archive functionality is enabled, this will output links to the date archives:

```html
<a href="/2025/05/" title="View all posts in May 2025">May</a> <a href="/2025/05/20/" title="View all posts on 20 May 2025">20</a>, <a href="/2025/" title="View all posts in 2025">2025</a>, 10:30 AM.
```

With microformats enabled, the output will include time tag:

```html
<time class="dt-published" datetime="2025-05-20T10:30:00+00:00">
  <a href="/2025/05/" title="View all posts in May 2025">May</a> <a href="/2025/05/20/" title="View all posts on 20 May 2025">20</a>, <a href="/2025/" title="View all posts in 2025">2025</a>, 10:30 AM.
</time>
```

With a custom link class:

```django
{% post_date link_class="date-link" %}
```

This will add the "date-link" class to all the date links.

### post_author

Return the author link for a post.

**Returns:** HTML with the author name and link, marked as safe.

#### post_author Parameters

- `outer_tag` (str): the outer tag that this should be wrapped in. Default is: "span".
- `outer_class` (str): the CSS classes to apply to the outer tag. Default: "".
- `link_class` (str): the CSS classes to apply to the link tag. Default: "".
- `pre_text` (str): the text to prepend to the author's name. Default: "".
- `post_text` (str): the text to append to the author's name. Default: "".

**Note:** `outer_tag` can be passed as a positional argument, but the other parameters must be passed as keyword arguments.

#### post_author Examples

```django
{% post_author %}
```

If author links are enabled, this will output:

```html
<a href="/author/samdoe/" title="View all posts by Sam Doe"><span class="p-author">Sam Doe</span></a>
```

If author links are disabled, this will output just the author name:

```html
<span class="p-author">Sam Doe</span>
```

The microformat class `p-author` will only be added if Microformats are enabled.

### post_categories

Returns a list of categories for a post.

**Returns:** HTML with the category link, marked as safe.

#### post_categories Parameters

- `outer_tag` (str): the outer tag that this should be wrapped in. Accepted options are "ul", "div", "span". If "ul" is used, then the inner items will be wrapped with "li" tags.
Default is: "ul".
- `outer_class` (str): the CSS classes to apply to the outer tag. Default: "".
- `link_class` (str): the CSS classes to apply to the link tag. Default: "".
- `separator` (str): the separator to use between categories. Only relevant when not using "ul" as the outer tag.
Default: ", ".
- `pre_text` (str): the text to prepend to the list of categories. Only relevant when not using "ul" as the outer tag.
Default: "".
- `post_text` (str): the text to append to the list of categories. Only relevant when not using "ul" as the outer tag.
Default: "".

**Note:** `outer_tag` can be passed as a positional argument, but the other parameters must be passed as keyword arguments.

#### post_categories Examples

```django
{% post_categories %}
```

```html
<ul>
  <li>
    <a href="/category/general/" title="View all posts in the General category">General</a>
  </li>
  <li>
    <a href="/category/news/" title="View all posts in the General category">News</a>
  </li>
</ul>
```

Wrapped in a `div` tag:

```django
{% post_categories "div" %}
```

```html
<div>
  <a href="/category/general/" title="View all posts in the General category">General</a>,
  <a href="/category/news/" title="View all posts in the General category">News</a>
</div>
```

Wrapped in a `span` tag with all optional parameters:

```django
{% post_categories "span" outer_class="class1" link_class="class2" separator=" | " pre_text="Categories: " post_text="." %}
```

```html
<span class="class1">Categories:
  <a href="/category/general/" title="View all posts in the General category" class="class2">General</a> | <a href="/category/news/" title="View all posts in the General category" class="class2">News</a>.
</span>
```

### post_tags

Returns a list of tags for a post.

**Returns:** HTML with the tag links, marked as safe.

#### post_tags Parameters

- `outer_tag` (str): the outer tag that this should be wrapped in. Accepted options are "ul", "div", "span". If "ul" is used, then the inner items will be wrapped with "li" tags.
Default is: "ul".
- `outer_class` (str): the CSS classes to apply to the outer tag. Default: "".
- `link_class` (str): the CSS classes to apply to the link tag. Default: "".
- `separator` (str): the separator to use between categories. Only relevant when not using "ul" as the outer tag.
Default: ", ".
- `pre_text` (str): the text to prepend to the list of categories. Only relevant when not using "ul" as the outer tag.
Default: "".
- `post_text` (str): the text to append to the list of categories. Only relevant when not using "ul" as the outer tag.
Default: "".

**Note:** `outer_tag` can be passed as a positional argument, but the other parameters must be passed as keyword arguments.

#### post_tags Examples

Just the tags, with no arguments.

```django
{% post_tags %}
```

Outputs a list of all tags:

```html
<ul>
  <li>
    <a href="/tag/python/" title="View all posts tagged with Python">Python</a>
  </li>
  <li>
    <a href="/tag/django/" title="View all posts tagged with Django">Django</a>
  </li>
</ul>
```

Wrapped in a `div` tag:

```django
{% post_tags "div" %}
```

```html
<div>
  <a href="/tag/python/" title="View all posts tagged with Python">Python</a>,
  <a href="/tag/django/" title="View all posts tagged with Django">Django</a>
</div>
```

Wrapped in a `span` tag with all optional parameters:

```django
{% post_tags "span" outer_class="class1" link_class="class2" separator=" | " pre_text="Tags: " post_text="." %}
```

```html
<span class="class1">Tags:
<a href="/tag/python/" title="View all posts tagged with Python" class="class2">Python</a> |
<a href="/tag/django/" title="View all posts tagged with Django" class="class2">Django</a>.
</span>
```

## Search Tags

These tags provide search functionality for your blog.

### search_form

Render a complete search form with customizable styling.

**Returns:** HTML form string, or empty string if search is disabled.

#### search_form Parameters

- `placeholder` (str): Placeholder text for the search input. Optional, default: "Search..."
- `button_text` (str): Text for the submit button. Optional, default: "Search"
- `form_class` (str): CSS class(es) for the form element. Optional.
- `input_class` (str): CSS class(es) for the input element. Optional.
- `button_class` (str): CSS class(es) for the button element. Optional.
- `show_button` (bool): Whether to show the submit button.  Optional, default: True

**Note:** all parameters must be passed as keyword arguments.

#### search_form Examples

Basic search form:

```django
{% search_form %}
```

This will output:

```html
<form action="/search/" method="get">
  <input type="search" name="q" value="" placeholder="Search..." aria-label="Search">
  <button type="submit">Search</button>
</form>
```

Customized search form:

```django
{% search_form placeholder="Find posts..." button_text="Go" form_class="search-form" input_class="form-control" button_class="btn btn-primary" %}
```

This will output:

```html
<form action="/search/" method="get" class="search-form">
  <input type="search" name="q" value="" placeholder="Find posts..." aria-label="Search" class="form-control">
  <button type="submit" class="btn btn-primary">Go</button>
</form>
```

Search form without button (for icon-based designs):

```django
{% search_form show_button=False %}
```

### search_errors

Display search validation errors from the current context.

**Returns:** HTML string with error messages, or empty string if no errors.

#### search_errors Parameters

- `outer_tag` (str): The outer HTML tag to wrap all errors. Allowed values: "div", "section", "aside", "article". Optional, default: "div"
- `outer_class` (str): The CSS class(es) for the outer tag. Optional, default: "search-errors"
- `error_tag` (str): The HTML tag for each error message. Allowed values: "p", "span", "div", "li". Optional, default: "p"
- `error_class` (str): The CSS class(es) for each error tag. Optional, default: "error"

**Note:** `outer_tag` can be passed as a positional argument, but the other parameters must be passed as keyword arguments.

#### search_errors Examples

Basic error display:

```django
{% search_errors %}
```

This will output:

```html
<div class="search-errors">
  <p class="error">Search query must be at least 3 characters.</p>
</div>
```

Customized error display:

```django
{% search_errors outer="section" outer_class="alert alert-danger" error_tag="div" error_class="error-message" %}
```

This will output:

```html
<section class="alert alert-danger">
  <div class="error-message">Search query must be at least 3 characters.</div>
</section>
```

## Utility Tags

These tags provide additional helper functions for your templates.

### category_title

Return the title of a category from the current context. Expects there to be a `category` object in the context.

**Returns:** string or HTML-formatted string with the category title.

#### category_title Parameters

- `outer_tag` (str): The outer HTML tag for the category. Allowed values: "h1", "h2", "h3", "h4", "h5", "h6", "p",
  "div", "span". Optional, if ommitted no outer tag will be used.
- `outer_class` (str): The CSS class(es) for the outer tag. Optional.
- `pre_text` (str): The text to prepend to the category title. Optional.
- `post_text` (str): The text to append to the category title. Optional.

**Note:** `outer_tag` can be passed as a positional argument, but the other parameters must be passed as keyword arguments.

#### category_title Examples

```django
{% category_title outer_tag="h1" outer_class="category-title" pre_text="Category: " %}
```

This will output:

```html
<h1 class="category-title">Category: General</h1>
```

### tag_title

Return the title of a tag from the current context.

**Returns:** string or HTML-formatted string with the tag title.

#### tag_title Parameters

- `outer_tag` (str): The outer HTML tag for the tag title. Allowed values: "h1", "h2", "h3", "h4", "h5", "h6", "p",
  "div", "span". Optional, if omitted, no outer tag will be used.
- `outer_class` (str): The CSS class(es) for the outer tag. Optional.
- `pre_text` (str): The text to prepend to the tag title. Optional.
- `post_text` (str): The text to append to the tag title. Optional.

**Note:** `outer_tag` can be passed as a positional argument, but the other parameters must be passed as keyword arguments.

#### tag_title Examples

```django
{% tag_title outer_tag="h1" outer_class="tag-title" pre_text="Posts tagged with: " %}
```

This will output:

```html
<h1 class="tag-title">Posts tagged with: Python</h1>
```

If multiple tags are in the context, they will be joined with commas:

```html
<h1 class="tag-title">Posts tagged with: Python, Django</h1>
```

### search_title

Return the title of a search query from the current context.

**Returns:** string or HTML-formatted string with the search query.

#### search_title Parameters

- `outer_tag` (str): The outer HTML tag for the search title. Allowed values: "h1", "h2", "h3", "h4", "h5", "h6", "p", "div", "span". Optional.
- `outer_class` (str): The CSS class(es) for the outer tag. Optional.
- `pre_text` (str): The text to prepend to the search query. Optional.
- `post_text` (str): The text to append to the search query. Optional.

**Note:** `outer_tag` can be passed as a positional argument, but the other parameters must be passed as keyword arguments.

#### search_title Examples

```django
{% search_title outer_tag="h1" outer_class="search-heading" pre_text="Search Results for '" post_text="'" %}
```

This will output:

```html
<h1 class="search-heading">Search Results for 'django'</h1>
```

### author_name

Return the name of an author from the current context. Expects there to be an `author` object in the context. If there is no `author` object, returns an empty string.

This is typically used on a page that displays the author's posts.

**Returns:** string or HTML-formatted string with the author's name.

#### author_name Parameters

- `outer_tag` (str): The outer HTML tag for the search title. Allowed values: "h1", "h2", "h3", "h4", "h5", "h6", "p", "div", "span". Optional.
- `outer_class` (str): The CSS class(es) for the outer tag. Optional.
- `pre_text` (str): The text to prepend to the search query. Optional.
- `post_text` (str): The text to append to the search query. Optional.

**Note:** `outer_tag` can be passed as a positional argument, but the other parameters must be passed as keyword arguments.

#### author_name Examples

```django
{% author_name outer_tag="h1" outer_class="title" pre_text="Posts written by '" post_text="'" %}
```

This will output:

```html
<h1 class="title">Posts written by 'Sam Doe'</h1>
```

### is_paginated

Returns whether the current page is paginated.

**Returns:** boolean

#### is_paginated Examples

```django
{% if is_paginated %}
    <p>There are more pages.</p>
{% endif %}
```

### pagination_links

Returns safely-marked HTML with simple links to the previous and next pages.

#### pagination_links Examples

If the `pagination_links` tag is used on the first page of a 10-page result set:

```django
{% pagination_links %}
```

```html
<span class="next">
  <a href="?page=2">next</a>
  <a href="?page=10">last &raquo;</a>
</span>
```

If the `pagination_links` tag is used on page 3 of a 10-page result set:

```django
{% pagination_links %}
```

```html
<span class="previous">
  <a href="?page=1">&laquo; first</a>
  <a href="?page=2">previous</a>
</span>
<span class="next">
  <a href="?page=4">next</a>
  <a href="?page=10">last &raquo;</a>
</span>
```

If the `pagination_links` tag is used on the last page of a 10-page result set:

```django
{% pagination_links %}
```

```html
<span class="previous">
  <a href="?page=1">&laquo; first</a>
  <a href="?page=9">previous</a>
</span>
```

### page_link

Returns a safely-marked HTML link to a specified page. If the page doesn't exist, an empty string is returned.

#### page_link Parameters

- `page_slug` (str): Slug of the page to link to. Required.
- `outer_tag` (str): HTML tag to wrap the link in. Optional, default: "span".
- `outer_class` (str): CSS class(es) for the outer tag. Optional.
- `link_class` (str): CSS class(es) for the link element. Optional.

**Note:** `page_slug` can be passed as a positional argument or a keyword argument. All other parameters must be passed
as keyword arguments.

#### page_link Examples

The `page_link` tag with no extra parameters:

```django
{% page_link "about" %}
```

```html
<a href="/about/">About</a>
```

The `page_link` tag with all extra parameters:

```django
{% page_link "about" outer_tag="div" outer_class="page-item" link_class="page-link" %}
```

```html
<div class="page-item">
  <a href="/about/" class="page-link">About</a>
</div>
```

### rss_link

Renders a `link` tag with the URL to the RSS feed on the page. Should be used in the `<head>` section of your HTML. If `RSS_ENABLED` is set to `False`, it will not render anything.

#### rss_link Examples

```django
{% rss_link %}
```

This will output:

```html
<link rel="alternate" type="application/rss+xml" title="Latest Posts" href="/rss/">
```

### post_wrap

This is block-style tag that wraps some HTML content with an HTML tag and an optional CSS class. Used to wrap the post content with an HTML tag, and will include the necessary microformats tags, if enabled.

#### post_wrap Parameters

- `tag` (str): HTML tag to wrap the content in. Required.
- `class` (str): CSS class(es) for the wrapper tag. Optional.

#### post_wrap Examples

The `post_wrap` tag with no extra parameters and microformats enabled:

```django
{% post_wrap "article" %}
  {% post_title outer_tag="h1" %}
  {% post_content %}
{% end_post_wrap %}
```

```html
<article class="h-entry">
  <h1>Post Title</h1>
  <p>Post content.</p>
</article>
```

The `post_wrap` tag with extra parameters and microformats enabled:

```django
{% post_wrap "article" class="post" %}
  {% post_title outer_tag="h1" %}
  {% post_content %}
{% end_post_wrap %}
```

```html
<article class="h-entry post">
  <h1>Post Title</h1>
  <p>Post content.</p>
</article>
```

### djpress_header

This tag should be included in the `head` section of your HTML. It will include any content that is registered with
plugins. For example, a plugin may need to include additional CSS or meta tags, and this tag will enable this.

#### djpress_header Examples

The `djpress_header` tag with no extra parameters:

```django
<head>
<!-- extra head content -->
{% djpress_header %}
</head>
```

By default this will not include any content unless you have enabled a plugin that registers content with this tag.

### djpress_footer

This tag should be included just before the closing `body` tag of your HTML. It will include any content that is
registered with plugins. For example, a plugin may need to include additional scripts or content, and this tag will
enable this.

#### djpress_footer Examples

The `djpress_footer` tag with no extra parameters:

```django
<!-- extra body content -->
{% djpress_footer %}
</body>
</html>
```

By default this will not include any content unless you have enabled a plugin that registers content with this tag.
