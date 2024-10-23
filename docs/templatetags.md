# Template Tags

To use any of the following tags, you must load the `djpress_tags` in your template file:

```django
{% load djpress_tags %}
```

## get_posts

Return all published posts as a queryset.

### Returns

A queryset of all published posts.

### Examples

This is useful for building an index page with all posts:

```django
{% get_posts as all_posts %}

{% for post in all_posts %}

<ul>
<li>{{ post.title }}</li>
</ul>

{% endfor %}
```

## blog_title

Returns the blog title as configured in the settings with the `BLOG_TITLE` variable. If no blog title has been configured, this will return the default title: "My DJ Press Blog".

### Returns

The `BLOG_TITLE` value as a string with no additional formatting.

### Examples

This is useful for the HTML `title` tag:

```django
<title>{% blog_title %}</title>
```

## blog_title_link

### Arguments

- `link_class` (optional): CSS class(es) to apply to the link.

### Returns

The blog title as configured in the settings with the `BLOG_TITLE` variable, but also wrapped with an HTML link to the index view. The output from this tag is the HTML link which has been marked as safe.

### Examples

Just the tag with no argument:

```django
{% blog_title_link %}
```

Outputs the following:

```html
<a href="/">My DJ Press Blog</a>
```

The tag with a positional argument:

```django
{% blog_title_link "mycssclass" %}
```

Outputs the following:

```html
<a href="/" class="mycssclass">My DJ Press Blog</a>
```

The tag with a named argument:

```django
{% blog_title_link link_class="mycssclass" %}
```

Outputs the following:

```html
<a href="/" class="mycssclass">My DJ Press Blog</a>
```

The `link_class` argument can contain multiple CSS tags separated by spaces:

```django
{% blog_title_link link_class="class1 class2" %}
```

Outputs the following:

```html
<a href="/" class="class1 class2">My DJ Press Blog</a>
```

## blog_page_title

Returns the title of the blog page, depending on the context of the page. A different title is returned for a category page, a blog page, author page, etc. This is useful to be used in the `<title>` tag of the template.

### Arguments

- `pre_text` (optional): text to be displayed before the page title
- `post_text` (optional): text to be displayed after the page title

### Returns

A string with no HTML formatting.

### Examples

The tag with no options for a single blog page or post:

```django
<title>{% blog_page_title %}</title>
````

Outputs the following:

```html
<title>My blog post title</title>
```

The tag can be combined with the `blog_title` tag as well as using the `post_text` field.

```django
<title>{% blog_page_title post_text=" | " %}{% blog_title %}</title>
```

Outputs the following:

```html
<title>My blog post title | My DJ Press Blog</title>
```

Or you can get creative with an emoji:

```django
<title>{% blog_page_title pre_text="🚀 " post_text=" | " %}{% blog_title %}</title>
```

Outputs the following:

```html
<title>🚀 My blog post title | My DJ Press Blog</title>
```

Category pages will show the title of the category, and author pages will show the display name of the author.

## get_pages

Get all published pages as an iterable queryset. This can be useful if you want to build your own menu or list of pages on the blog.

### Returns

An iterable queryset of published pages that are sorted by the `menu_order` field, and then by the `title` field.

### Examples

Get the pages and display as a list:

```django
{% get_pages as pages %}
<ul>
  {% for page in pages %}
    <li>
      <a href="{% url 'djpress:single_post' page.slug %}>{{ page.title }}</a>
    </li>
  {% endfor %}
</ul>
```

Outputs the following:

```html
<ul>
  <li>
    <a href="/about">About me</a>
  </li>
  <li>
    <a href="/contact">Contact me</a>
  </li>
</ul>
```

Also see `blog_pages` for a tag that produces similar output to the above but with just a single template tag.

## get_categories

Get all categories as an iterable queryset. This can be useful if you want to build your own menu or list of categories on the blog.

Also see `blog_categories` for a tag that produces similar output to the below example, but with just a single template tag.

### Return

An iterable queryset of published pages that are sorted by the `menu_order` field, and then by the `title` field.

### Examples

Get the categories and display as a list:

```django
{% get_categories as categories %}
<ul>
  {% for category in categories %}
    <li>
      <a href="{% url 'djpress:category_posts' category.slug %}>{{ category.title }}</a>
    </li>
  {% endfor %}
</ul>
```

Outputs the following:

```html
<ul>
  <li>
    <a href="/category/general">General</a>
  </li>
  <li>
    <a href="/category/news">News</a>
  </li>
</ul>
```

## blog_categories

Get a list of all categories wrapped in HTML that can be configured with optional arguments.

### Arguments

- `outer` (optional): the outer tags that this should be wrapped in. Accepted options are "ul", "div", "span". Default is: "ul".
- `outer_class` (optional): the CSS classes to apply to the outer tag. Default: "".
- `link_class` (optional): the CSS classes to apply to the link tag. Default: "".

### Returns

All categories as HTML which has been marked as safe.

### Examples

Just the tag, with no arguments.

```django
{% blog_categories %}
```

This will output the same HTML from the `get_categories` example.

```html
<ul>
  <li>
    <a href="/category/general" title="View all posts in the General category">General</a>
  </li>
  <li>
    <a href="/category/news" title="View all posts in the General category">News</a>
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
  <a href="/category/general" title="View all posts in the General category" class="class2">General</a>,
  <a href="/category/news" title="View all posts in the General category" class="class2">News</a>
</div>
```

Wrapped in a `span` tag with classes added, using named arguments.

```django
{% blog_categories outer="div" outer_class="class1" link_class="class2" %}
```

Outputs the same comma-separated list of categories, but wrapped in a `span` tag.

```html
<span class="class1">
  <a href="/category/general" title="View all posts in the General category" class="class2">General</a>,
  <a href="/category/news" title="View all posts in the General category" class="class2">News</a>
</span>
```

## blog_pages

Get all blog pages as a single-level list, wrapped in HTML that can be configured with optional arguments.

### Arguments

- `outer` (optional): the outer tags that this should be wrapped in. Accepted options are "ul", "div", "span". Default is: "ul".
- `outer_class` (optional): the CSS classes to apply to the outer tag. Default: "".
- `link_class` (optional): the CSS classes to apply to the link tag. Default: "".

The output from this tag is HTML which has been marked as safe.

### Examples

Just the tag, with no arguments.

```django
{% blog_pages %}
```

This will output the same HTML from the `get_pages` example.

```html
<ul>
  <li>
    <a href="/about">About me</a>
  </li>
  <li>
    <a href="/contact">Contact me</a>
  </li>
</ul>
```

Wrapped in a `div` tag with classes added, using positional arguments.

```django
{% blog_pages "div" "class1" "class2" %}
```

Outputs a comma-separated list of pages, wrapped in a `div` tag.

```html
<div class="class1">
  <a href="/about" class="class2">About me</a>,
  <a href="/contact" class="class2">Contact me</a>
</div>
```

Wrapped in a `span` tag with classes added, using named arguments.

```django
{% blog_pages outer="div" outer_class="class1" link_class="class2" %}
```

Outputs the same comma-separated list of pages, but wrapped in a `span` tag.

```html
<span class="class1">
  <a href="/about" class="class2">About me</a>,
  <a href="/contact" class="class2">Contact me</a>
</span>
```

## blog_pages_list

Get all published blog pages and output as a nested list to support parent pages.

### Arguments

- `ul_outer_class` (optional): The CSS class(es) for the outer unordered list.
- `li_class` (optional): The CSS class(es) for the list item tags
- `a_class` (optional): The CSS class(es) for the anchor tags.
- `ul_child_class` (optional): The CSS class(es) for the nested unordered lists.

The output from this tag is HTML which has been marked as safe.

### Examples

Just the tag, with no arguments.

```django
{% blog_pages %}
```

This will output the following HTML:

```html
<ul>
  <li>
    <a href="/about">About me</a>
    <ul>
      <li>
        <a href="/about/hobbies">Hobbies</a>
      </li>
      <li>
        <a href="/about/resume">My Resume</a>
      </li>
    </ul>
  </li>
  <li>
    <a href="/contact">Contact me</a>
  </li>
</ul>
```

Or arguments can be used to build a Bootstrap-like navbar menu.

```django
{% blog_pages ul_outer_class="navbar-nav" li_class="nav-item" a_class="nav-link" ul_child_class="dropdown-menu" %}
```

This will output the following HTML:

```html
<ul class="navbar-nav">
  <li class="nav-item">
    <a href="/about" title="View the About me page" class="nav-link">About me</a>
    <ul>
      <li class="nav-item">
        <a href="/about/hobbies" title="View the Hobbies page" class="nav-link">Hobbies</a>
      </li>
      <li class="nav-item">
        <a href="/about/resume" title="View the My Resume page" class="nav-link">My Resume</a>
      </li>
    </ul>
  </li>
  <li class="nav-item">
    <a href="/contact" title="View the Contact me page" class="nav-link">Contact me</a>
  </li>
</ul>
```


## have_posts

Get a list of posts from the current context. This always returns a list, even if the context only contains a single post or page.

This is useful if you want to use a single template to show either a single post or a collection of posts.

### Returns

A list containing a single Post object, a Page object of posts, or an empty list.

### Examples

```django
{% have_posts as posts %}

{% for post in posts %}
    <h2>{{ post.title }}</h2>
    <p>{{ post.excerpt }}</p>
{% endfor %}
```

## get_post_title

Returns the title of the current post as a plain string.

### Returns

A string containing the post title or empty if there's no post in the context.

### Examples

```django
<h1>{% get_post_title %}</h1>
```

Outputs:

```html
<h1>My Post Title</h1>
```

## post_wrap

This is a wrapper tag that is used to add a semantic HTML wrapper tags around a post. By default this will use an
`<article>` tag and will add the necessary microformat tags if microformats are enabled (these are enabled by
default.)

### Arguments

*Note* - keyword arguments are recommended but not required.

- `tag` (optional): The HTML tag to wrap the content in, default is `<article>`.
- `class` (optional): CSS class(es) to apply to the tag, default is blank.

### Usage

Basic wrapper with no additional arguments and with microformats enabled.

```django
{% post_wrap %}
<h2>Post Title</h2>
<p>This is my post content</p>
{% end_post_wrap %}
```

Outputs:

```django
<article class="h-entry">
<h2>Post Title</h2>
<p>This is my post content</p>
</article>
```

Wrapper with specific HTML tag, a CSS class, and with microformats enabled.

```django
{% post_wrap tag="div" class="blogpost" %}
<h2>Post Title</h2>
<p>This is my post content</p>
{% end_post_wrap %}
```

Outputs:

```django
<div class="h-entry blogpost">
<h2>Post Title</h2>
<p>This is my post content</p>
</div>
```

## post_title

Returns the title of the current post as a link if it's part of a collection, or just the title if it's single post.

The `force_link` argument can be used to always return the link, regardless if it's part of a collection or not.

### Arguments

*Note* - these are keyword-only arguments.

- `outer_tag` (optional): The outer HTML tag to wrap the title in.
- `link_class` (optional): CSS class(es) to apply to the link.
- `force_link` (optional, boolean): Always displays a link when true.

### Returns

A string containing just the post title, or HTML text that has been marked as safe.

### Examples

```django
{% post_title %}
```

If a single post, this outputs:

```html
My Post Title
```

Or, if part of a collection of posts:

```html
<a href="/my-post/">My Post Title</a>
```

With the `link_class` argument:

```django
{% post_title link_class="post-title-link" %}
```

Outputs:

```html
<a href="/my-post/" class="post-title-link">My Post Title</a>
```

Or, to force the link, even when just a single post is displayed:

```django
{% post_title force_link=True %}
```

Outputs:

```html
<a href="/my-post/">My Post Title</a>
```

To wrap the title in an HTML tag, use the `outer_tag` attribute. If microformats are enabled (these are enabled by
default), then a class is added to the outer tag. The outer tag must be one of the following types:
"h1", "h2", "h3", "h4", "h5", "h6", "p", "div", "span".
If anything else is used, or if the outer_tag attribute is ommitted, then no outer tag is added.

```django
{% post_title outer_tag="h2" %}
```

Outputs:

```html
<h2 class="p-name"><a href="/my-post/">My Post Title</a></h2>
```

## get_post_author

Returns the display name of the post's author.

### Returns

String containing the author's display name.

### Examples

```django
<p>Written by {% get_post_author %}</p>
```

Outputs:

```html
<p>Written by Sam Doe</p>
```

## post_author

Get the author's display name, wrapped in a span tag, with a link to their author page.

### Arguments

- `link_class` (optional): CSS class(es) to apply to the link.

### Returns

HTML text containing the author's name, marked as safe.

### Examples

```django
<p>By {% post_author %}</p>
```

Outputs:

```html
<p>By <a href="/post-author/" title="View all posts by Post Author"><span rel="author">Post Author</span></a></p>
```

With the `link_class` argument:

```django
<p>By {% post_author link_class="author-link" %}</p>
```

Outputs:

```html
<p>By <a href="/post-author/" title="View all posts by Post Author" class="author-link"><span rel="author">Post Author</span></a></p>
```

## post_category_link

Get a link to a post's category.

### Arguments

- `category`: The Category object to link to.
- `link_class` (optional): CSS class(es) to apply to the link.

### Returns

HTML text containing a link to the category.

### Examples

```django
{% for category in post.categories.all %}
    {% post_category_link category link_class="category-link" %}
{% endfor %}
```

## get_post_date

Get the date of the current post.

### Returns

A string containing the post's date formatted as "MMM D, YYYY".

### Examples

```django
<p>Published on {% get_post_date %}</p>
```

Outputs:

```html
<p>Published on Jun 5, 2024</p>
```

## post_date_link

Returns the post's date as a set of links to date-based archives, if enabled.

### Arguments

- `link_class` (optional): CSS class(es) to apply to the links.

### Returns

An HTML string containing links to date-based archives, or just the formatted date if date archives are disabled.

### Examples

```django
<p>Posted on {% post_date_link link_class="date-link" %}</p>
```

Outputs:

```html
<p>Posted on <a href="/archives/2024/06/" title="View all posts in Jun 2024">Jun</a> <a href="/archives/2024/06/05/" title="View all posts on 5 Jun 2024">5</a>, <a href="/archives/2024/" title="View all posts in 2024">2024</a>, 11:06 AM.</p>
```

## post_content

Returns the content of the current post, either full or truncated with a "read more" link. If the post is on a post detail page, the full content is displayed. If the post is on any other type of page, just the truncated content is displayed.

### Arguments

*Note* - these are keyword-only arguments.

- `outer_tag` (optional):
- `read_more_link_class` (optional): CSS class(es) to apply to the "read more" link.
- `read_more_text` (optional): Custom text for the "read more" link.

### Returns

HTML text containing the post content, or truncated with a "read more" link. The HTML is marked as safe.

### Examples

```django
{% post_content %}
```

If the post is on a detail page, this will output the full content. But if the post is part of a collection of posts, it will only display truncated content with a read more link:

```html
<p>This is the start of the post content.</p>
<p><a href="/post-title/">Read more...</a></p>
```

With the optional arguments to control the read more function:

```django
{% post_content read_more_link_class="read-more" read_more_text="Continue reading..." %}
```

Outputs:

```html
<p>This is the start of the post content.</p>
<p><a href="/post-title/" class="read-more">Continue reading...</a></p>
```

To wrap the content in an HTML tag, use the `outer_tag` attribute. Note that if microformats are enabled (these are
enabled by default), then `e-content` will be added to the outer tag class.

```django
{% post_content outer_tag="section" %}
```

Outputs:

```html
<section class="e-content">
<p>This is the start of the post content.</p>
<p><a href="/post-title/" class="read-more">Continue reading...</a></p>
</section>
```

## category_title

Get the title of the current category, optionally wrapped in an HTML tag.

### Arguments

- `outer` (optional): The HTML tag to wrap the title in.
- `outer_class` (optional): CSS class(es) to apply to the outer tag.
- `pre_text` (optional): Text to prepend to the category title.
- `post_text` (optional): Text to append to the category title.

### Returns

A string or HTML-wrapped text containing the category title. The HTML text is marked as safe.

### Examples

The following will just return the category title as a string:

```django
{% category_title %}
```

The following will return HTML text:

```django
{% category_title outer="h1" outer_class="category-title" pre_text="Category: " %}
```

Outputs:

```html
<h1 class="category-title">Category: General</h1>
```

Or with all arguments:

```django
{% category_title outer="h1" outer_class="category-title" pre_text="Posts in the '" post_text="' category" %}
```

Outputs:

```html
<h1 class="category-title">Posts in the 'General' category</h1>
```

## author_name

Get the author's display name, optionally wrapped in an HTML tag.

### Arguments

- `outer` (optional): The HTML tag to wrap the name in.
- `outer_class` (optional): CSS class(es) to apply to the outer tag.
- `pre_text` (optional): Text to prepend to the author name.
- `post_text` (optional): Text to append to the author name.

### Returns

A string or HTML-wrapped text containing the author's display name. The HTML text is marked as safe.

### Examples

The following will just return the author's display name

```django
{% author_name %}
```

The following will return HTML text:

```django
{% author_name outer="h1" outer_class="author-title" pre_text="Author: " %}
```

Outputs:

```html
<h1 class="author-title">Author: Sam Jones</h1>
```

Or with all arguments:

```django
{% author_name outer="h1" outer_class="author-title" pre_text="Posts that '" post_text="' wrote" %}
```

Outputs:

```html
<h1 class="author-title">Posts that 'Sam Jones' wrote</h1>
```

## post_categories_link

Returns a list of links to the categories of the current post.

### Arguments

- `outer` (optional): The HTML tag to use for the outer container. Default is "ul".
- `outer_class` (optional): CSS class(es) to apply to the outer container.
- `link_class` (optional): CSS class(es) to apply to each category link.

### Returns

An HTML string containing a list of category links for the current post.

### Examples

Just the tag with no arguments:

```django
{% post_categories_link %}
```

Outputs:

```html
<ul>
  <li>
    <a href="/general/" title="View all posts in the General category">General</a>
  </li>
</ul>
```

The tag with all options provided as arguments and using a `div` for the outer tag:

```django
{% post_categories_link outer="div" outer_class="post-categories" link_class="category-link" %}
```

Outputs the following HTML:

```html
<div class="post-categories">
  <a href="/general/" title="View all posts in the General category" class="category-link">General</a>
</div>
```

The tag with a `span` for the outer tag:

```django
{% post_categories_link outer="span" %}
```

Outputs the following HTML:

```html
<span>
  <a href="/general/" title="View all posts in the General category">General</a>
</span>
```

## pagination_links

This is used to create basic pagination links in the form of "Page x of y" with left and right angled quotes on either side to allow moving backwards and forwards through the pages.

This tag will be ignored if the current view is not a paginated object.

For more control over pagination links, you can create your own pagination controls with the following tags:

- `is_paginated`
- `get_pagination_range`
- `get_pagination_range`
- `get_pagination_current_page`

### Returns

An HTML string containing pagination links.

### Examples

If used on the first page of three:

```django
{% pagination_links %}
```

Outputs:

```html
<div class="pagination">
  <span class="current">
    Page 1 of 3
  </span>
  <span class="next">
    <a href="?page=2">next</a> <a href="?page=3">last »</a>
  </span>
</div>
```

If used on the second page of three:

```django
{% pagination_links %}
```

Outputs:

```html
<div class="pagination">
  <span class="previous">
    <a href="?page=1">« first</a> <a href="?page=1">previous</a>
  </span>
  <span class="current">Page 2 of 3</span>
  <span class="next">
    <a href="?page=3">next</a> <a href="?page=3">last »</a>
  </span>
</div>
```

If used on the third page of three:

```django
{% pagination_links %}
```

Outputs:

```html
<div class="pagination">
  <span class="previous">
    <a href="?page=1">« first</a> <a href="?page=2">previous</a>
  </span>
  <span class="current">Page 3 of 3</span>
</div>
```

If used on paginated page with only one page:

```django
{% pagination_links %}
```

Outputs:

```html
<div class="pagination">
  <span class="current">Page 1 of 1</span>
</div>
```

## is_paginated

Returns whether the current posts are paginated.

### Returns

A boolean indicating if the posts are paginated.

### Examples

```django
{% if is_paginated %}
    <!-- Show pagination controls -->
{% endif %}
```

## get_pagination_range

Returns the range of pagination pages.

### Returns

A range object representing the pagination pages.

### Examples

```django
{% for page_num in get_pagination_range %}
    <a href="?page={{ page_num }}">{{ page_num }}</a>
{% endfor %}
```

## get_pagination_current_page

Returns the current page number.

### Returns

An integer representing the current page number.

### Examples

```django
<p>You are on page {% get_pagination_current_page %}</p>
```

## page_link

Returns a link to a specific page.

### Arguments

- `page_slug`: The slug of the page to link to.
- `outer` (optional): The HTML tag to wrap the link in. Default is "div".
- `outer_class` (optional): CSS class(es) to apply to the outer tag.
- `link_class` (optional): CSS class(es) to apply to the link.

### Returns

An HTML string containing a link to the specified page.

### Examples

```django
{% page_link "about" %}
{% page_link "contact" outer="li" outer_class="menu-item" link_class="page-link" %}
```

## rss_url

Returns the URL of the RSS feed.

### Arguments

None

### Returns

A plain text representation of the URL.

### Examples

```django
<a href="{% rss_url %}">RSS Feed</a>

<link rel="alternate" type="application/rss+xml" title="Latest Posts" href="{% rss_url %}">
```
