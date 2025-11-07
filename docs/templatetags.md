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
2. **Display Tags** - Format and display data with appropriate HTML (e.g., `site_title_link`, `blog_categories`)
3. **Post Content Tags** - Handle rendering post content, titles, dates, etc. (e.g., `post_title`, `post_content`)
4. **Navigation Tags** - Generate navigation elements like menus (e.g., `site_pages_list`, `blog_categories`)
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
but apply your own custom formatting.

### get_posts

Returns all published posts as a queryset. Use this tag to access all published blog posts in your templates.

**Returns:** queryset of all published posts.

> **Related Topics:** See [url_structure.md](url_structure.md) for URL patterns and [themes.md](themes.md) for how to
> use posts in your theme.

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

Returns the most recent published posts. Tries to be efficient by checking if there's a `posts` object in the context
that can be used.

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

Get all published pages as an iterable queryset. This can be useful if you want to build your own menu or list of pages
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

Also see [`site_pages`](#site_pages) for a tag that produces similar output to the above but with just a single
template tag.

### get_categories

Get all categories as an iterable queryset. This can be useful if you want to build your own menu or list of categories
on the blog.

Also see `blog_categories` for a tag that produces similar output to the below example, but with just a single template
tag.

**Returns:** queryset of categories that are sorted by the `menu_order` field, and then by the `title` field.

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

**Returns:** string - the title of the post.

#### get_post_title Example

```django
{% get_post_title as title %}
<meta property="og:title" content="{{ title }}">
```

### get_post_url

Returns the URL of a post from the current context.

**Returns:** string - the URL of the post.

#### get_post_url Example

```django
{% get_post_url as post_url %}
<meta property="og:url" content="{{ post_url }}">
```

### get_post_author

Returns the author display name from the current context.

**Returns:** string - the author display name.

#### get_post_author Example

```django
{% get_post_author as author %}
<meta property="article:author" content="{{ author }}">
```

### get_post_date

Returns the date of a post from the current context.

**Returns:** string - the date of the post in the format "Mon DD, YYYY".

#### get_post_date Example

```django
{% get_post_date as post_date %}
<meta property="article:published_time" content="{{ post_date }}">
```

## Display Tags

These tags retrieve data and format it with HTML, ready to be displayed in your templates.

### site_title

Returns the site title as configured in the settings with the `SITE_TITLE` variable. If no site title has been
configured, this will return the default title: "My DJ Press Blog".

**Returns:** the `SITE_TITLE` value as a string.

> **Related Topics:** See [configuration.md](configuration.md) for how to configure the site title and other settings.

#### site_title Example

This is useful for the HTML `title` tag:

```django
<title>{% site_title %}</title>
```

### site_title_link

This is used to return an HTML link to the index view of the blog.

**Returns:** an HTML link to the index view marked as safe.

#### site_title_link Parameters

- `link_class` (optional): CSS class(es) to apply to the link.

#### site_title_link Examples

Just the tag with no argument:

```django
{% site_title_link %}
```

Outputs the following:

```html
<a href="/">My DJ Press Blog</a>
```

The tag with a positional argument:

```django
{% site_title_link "mycssclass" %}
```

Outputs the following:

```html
<a href="/" class="mycssclass">My DJ Press Blog</a>
```

The tag with a keyword argument:

```django
{% site_title_link link_class="mycssclass" %}
```

Outputs the following:

```html
<a href="/" class="mycssclass">My DJ Press Blog</a>
```

The `link_class` argument can contain multiple CSS tags separated by spaces:

```django
{% site_title_link link_class="class1 class2" %}
```

Outputs the following:

```html
<a href="/" class="class1 class2">My DJ Press Blog</a>
```

### page_title

Returns the title of the page, depending on the context of the page. A different title is returned for a category page,
a blog page, author page, etc. This is useful to be used in the `<title>` tag of the template.

**Returns:** A string with no HTML formatting.

#### page_title Parameters

- `pre_text` (optional): text to be displayed before the page title
- `post_text` (optional): text to be displayed after the page title

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

## Navigation Tags

These tags help you build navigation elements for your blog.

### blog_categories

Get a list of all categories wrapped in HTML that can be configured with optional arguments.

**Returns:** all categories as HTML which has been marked as safe.

> **Related Topics:** See [url_structure.md](url_structure.md) for category URL patterns and [configuration.md](configuration.md) for category-related settings.

#### blog_categories Parameters

- `outer_tag` (optional): the outer tags that this should be wrapped in. Accepted options are "ul", "div", "span".
  Default is: "ul".
- `outer_class` (optional): the CSS classes to apply to the outer tag. Default: "".
- `link_class` (optional): the CSS classes to apply to the link tag. Default: "".

#### blog_categories Examples

Just the tag, with no arguments.

```django
{% blog_categories %}
```

This will output:

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

Wrapped in a `div` tag with classes added, using positional arguments.

```django
{% blog_categories "div" "class1" "class2" %}
```

Outputs a comma-separated list of categories, wrapped in a `div` tag.

```html
<div class="class1">
  <a href="/category/general/" title="View all posts in the General category" class="class2">General</a>,
  <a href="/category/news/" title="View all posts in the General category" class="class2">News</a>
</div>
```

Wrapped in a `span` tag with classes added, using named arguments.

```django
{% blog_categories outer_tag="span" outer_class="class1" link_class="class2" %}
```

Outputs the same comma-separated list of categories, but wrapped in a `span` tag.

```html
<span class="class1">
  <a href="/category/general/" title="View all posts in the General category" class="class2">General</a>,
  <a href="/category/news/" title="View all posts in the General category" class="class2">News</a>
</span>
```

### blog_tags

Get a list of all tags wrapped in HTML that can be configured with optional arguments.

**Returns:** all tags as HTML which has been marked as safe.

> **Related Topics:** See [tags.md](tags.md) for more information about tags and [url_structure.md](url_structure.md)
for tag URL patterns.

#### blog_tags Parameters

- `outer_tag` (optional): the outer tags that this should be wrapped in. Accepted options are "ul", "div", "span".
  Default is: "ul".
- `outer_class` (optional): the CSS classes to apply to the outer tag. Default: "".
- `link_class` (optional): the CSS classes to apply to the link tag. Default: "".

#### blog_tags Examples

Just the tag, with no arguments.

```django
{% blog_tags %}
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

Wrapped in a `div` tag with classes added, using positional arguments.

```django
{% blog_tags "div" "tag-list" "tag-link" %}
```

Outputs a comma-separated list of tags, wrapped in a `div` tag.

```html
<div class="tag-list">
  <a href="/tag/python/" title="View all posts tagged with Python" class="tag-link">Python</a>,
  <a href="/tag/django/" title="View all posts tagged with Django" class="tag-link">Django</a>
</div>
```

Wrapped in a `span` tag with classes added, using named arguments.

```django
{% blog_tags outer_tag="span" outer_class="tag-list" link_class="tag-link" %}
```

Outputs the same comma-separated list of tags, but wrapped in a `span` tag.

```html
<span class="tag-list">
  <a href="/tag/python/" title="View all posts tagged with Python" class="tag-link">Python</a>,
  <a href="/tag/django/" title="View all posts tagged with Django" class="tag-link">Django</a>
</span>
```

### tags_with_counts

Get a list of all tags with post counts wrapped in HTML that can be configured with optional arguments.

**Returns:** all tags with post counts as HTML which has been marked as safe.

#### tags_with_counts Parameters

- `outer_tag` (optional): the outer tags that this should be wrapped in. Accepted options are "ul", "div", "span".
  Default is: "ul".
- `outer_class` (optional): the CSS classes to apply to the outer tag. Default: "".
- `link_class` (optional): the CSS classes to apply to the link tag. Default: "".

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

- `outer` (optional): the outer tags that this should be wrapped in. Accepted options are "ul", "div", "span". Default
  is: "ul".
- `outer_class` (optional): the CSS classes to apply to the outer tag. Default: "".
- `link_class` (optional): the CSS classes to apply to the link tag. Default: "".

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

- `ul_outer_class` (optional): The CSS class(es) for the outer unordered list.
- `li_class` (optional): The CSS class(es) for the list item tags
- `a_class` (optional): The CSS class(es) for the anchor tags.
- `ul_child_class` (optional): The CSS class(es) for the nested unordered lists.

#### site_pages_list Examples

Just the tag, with no arguments.

```django
{% site_pages_list %}
```

This will output the following HTML:

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

With CSS classes:

```django
{% site_pages_list ul_outer_class="main-nav" li_class="nav-item" a_class="nav-link" ul_child_class="sub-nav" %}
```

This will output:

```html
<ul class="main-nav">
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

These tags help you display the content of posts.

### post_title

Display the title of a post, with intelligent handling of linking depending on the context.

- In a single post view, displays just the title with no link.
- In a posts list view, displays the title with a link to the full post.

**Returns:** HTML with the post title, marked as safe.

> **Related Topics:** See [themes.md](themes.md) for more about post display in templates and [url_structure.md](url_structure.md) for post URL patterns.

#### post_title Parameters

- `outer_tag` (optional): The outer HTML tag for the title. Accepted options are "h1", "h2", "h3", "h4", "h5", "h6",
  "p", "div", "span". If not provided, no outer tag is used.
- `link_class` (optional): The CSS class(es) to apply to the link if the title is linked.
- `force_link` (optional): Boolean. If true, always links the title even in a single post view. Default is false.
- `include_empty` (optional): Boolean. If true, includes the title even if it is empty, using the post_title property
  fallback. Default is false.

#### post_title Exampless

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

- `outer_tag` (optional): The outer HTML tag to wrap the content in. Accepted options are "section", "div", "article",
  "p", "span". If not provided, no outer tag is used.
- `read_more_link_class` (optional): The CSS class(es) to apply to the "read more" link.
- `read_more_text` (optional): The text to use for the "read more" link. If not provided, defaults to "Read more".

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

- `link_class` (optional): The CSS class(es) to apply to the date links.

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

- `link_class` (optional): The CSS class(es) to apply to the link.

#### post_author Examples

```django
{% post_author %}
```

If author links are enabled, this will output:

```html
<a href="/author/johndoe/" title="View all posts by John Doe"><span class="p-author">John Doe</span></a>
```

If author links are disabled, this will output just the author name:

```html
<span class="p-author">John Doe</span>
```

The microformat class `p-author` will only be added if Microformats are enabled.

### post_category_link

Return the category link for a post.

**Returns:** HTML with the category link, marked as safe.

#### post_category_link Parameters

- `category`: The category object of the post.
- `link_class` (optional): The CSS class(es) to apply to the link.

#### post_category_link Examples

```django
{% for category in post.categories.all %}
  {% post_category_link category %}
{% endfor %}
```

If category functionality is disabled, this will output just the category name:

```html
General
```

If category functionality is enabled, this will output a link to the category:

```html
<a href="/category/general/" title="View all posts in the General category">General</a>
```

## Search Tags

These tags provide search functionality for your blog.

### search_url

Return the URL for the search page.

**Returns:** string with the search URL, or empty string if search is disabled.

#### search_url Example

```django
<form action="{% search_url %}" method="get">
  <input type="search" name="q" placeholder="Search...">
  <button type="submit">Search</button>
</form>
```

This will output:

```html
<form action="/search/" method="get">
  <input type="search" name="q" placeholder="Search...">
  <button type="submit">Search</button>
</form>
```

### search_form

Render a complete search form with customizable styling.

**Returns:** HTML form string, or empty string if search is disabled.

#### search_form Parameters

- `placeholder` (optional): Placeholder text for the search input. Default: "Search..."
- `button_text` (optional): Text for the submit button. Default: "Search"
- `form_class` (optional): CSS class(es) for the form element.
- `input_class` (optional): CSS class(es) for the input element.
- `button_class` (optional): CSS class(es) for the button element.
- `show_button` (optional): Whether to show the submit button. Default: True

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

### search_title

Return the title of a search query from the current context.

**Returns:** string or HTML-formatted string with the search query.

#### search_title Parameters

- `outer` (optional): The outer HTML tag for the search title. Allowed values: "h1", "h2", "h3", "h4", "h5", "h6", "p", "div", "span".
- `outer_class` (optional): The CSS class(es) for the outer tag.
- `pre_text` (optional): The text to prepend to the search query.
- `post_text` (optional): The text to append to the search query.

#### search_title Examples

```django
{% search_title outer="h1" outer_class="search-heading" pre_text="Search Results for '" post_text="'" %}
```

This will output:

```html
<h1 class="search-heading">Search Results for 'django'</h1>
```

### search_errors

Display search validation errors from the current context.

**Returns:** HTML string with error messages, or empty string if no errors.

#### search_errors Parameters

- `outer` (optional): The outer HTML tag to wrap all errors. Allowed values: "div", "section", "aside", "article". Default: "div"
- `outer_class` (optional): The CSS class(es) for the outer tag. Default: "search-errors"
- `error_tag` (optional): The HTML tag for each error message. Allowed values: "p", "span", "div", "li". Default: "p"
- `error_class` (optional): The CSS class(es) for each error tag. Default: "error"

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

### have_posts

Return the posts in the context, providing a convenient way to check if there are posts to display.

**Returns:** list of Post objects or a Page object of posts.

#### have_posts Example

```django
{% have_posts as posts_list %}
{% if posts_list %}
  <h2>We have posts!</h2>
  {% for post in posts_list %}
    <h3>{{ post.title }}</h3>
  {% endfor %}
{% else %}
  <p>No posts to display.</p>
{% endif %}
```

### category_title

Return the title of a category from the current context.

**Returns:** string or HTML-formatted string with the category title.

#### category_title Parameters

- `outer` (optional): The outer HTML tag for the category. Allowed values: "h1", "h2", "h3", "h4", "h5", "h6", "p",
  "div", "span".
- `outer_class` (optional): The CSS class(es) for the outer tag.
- `pre_text` (optional): The text to prepend to the category title.
- `post_text` (optional): The text to append to the category title.

#### category_title Examples

```django
{% category_title outer="h1" outer_class="category-title" pre_text="Category: " %}
```

This will output:

```html
<h1 class="category-title">Category: General</h1>
```

### tag_title

Return the title of a tag from the current context.

**Returns:** string or HTML-formatted string with the tag title.

#### tag_title Parameters

- `outer` (optional): The outer HTML tag for the tag title. Allowed values: "h1", "h2", "h3", "h4", "h5", "h6", "p",
  "div", "span".
- `outer_class` (optional): The CSS class(es) for the outer tag.
- `pre_text` (optional): The text to prepend to the tag title.
- `post_text` (optional): The text to append to the tag title.

#### tag_title Examples

```django
{% tag_title outer="h1" outer_class="tag-title" pre_text="Posts tagged with: " %}
```

This will output:

```html
<h1 class="tag-title">Posts tagged with: Python</h1>
```

If multiple tags are in the context, they will be joined with commas:

```html
<h1 class="tag-title">Posts tagged with: Python, Django</h1>
```
