# Themes

A DJ Press theme is a collection of one or more Django template files. and any static files required to style those
templates.

## Template Files

Template files should be copied to: `./templates/djpress/{{ your_theme_name }}/`. At a minimum, the theme must include
an `index.html` file. You can build an entire theme with just this one file, and an example can be seen in the DJ Press
included theme called `default`.

Other template files that can be included are as follows:

- `home.html` - used on the home page view, i.e. `https://yourblog.com/`
- `archives.html` - used to display the date-based archives views, e.g. `https://yourblog.com/2024/`
- `category.html` - used to display blog posts in a particular category, e.g. `https://yourblog.com/category/news/`
- `author.html` - used to display blog posts by a particular author, e.g. `https://yourblog.com/author/sam/`
- `single.html` - used to display a single blog post, e.g. `https://yourblog.com/2024/09/30/my-interesting-blog-post/`
- `page.html` - used to display a single page, e.g. `https://yourblog.com/colophon/`

In all cases, if the above file is not found, the `index.html` page will be displayed instead.

## Static Files

Static files should be copied to: `./static/djpress/{{ your_theme_name }}/`. Static files are typically grouped into
sub-directories for CSS or JavaScript or image files, e.g. `./static/djpress/{{ your_theme_name }}/css/` or
`./static/djpress/{{ your_theme_name }}/js/` or `./static/djpress/{{ your_theme_name }}/img`, but these
sub-directories are optional and up to the theme developer how or if to use them.

From within the template files, static assets can be referenced using standard Django template tags, e.g.
`{% static 'djpress/{{ your_theme_name }}/css/style.css' %}`, depending on the aforementioned directory structure.

## Configure a Theme

In your Django project settings file, configure the `THEME` setting in the `DJPRESS_SETTINGS` object, e.g.

```python
DJPRESS_SETTINGS = {
  "THEME": "your_theme_name",
}
```

In the example configuration, `your_theme_name` must match exactly the directory name that the theme's template files
are copied to. If this directory cannot be found, or if there is no matching template file in it, your site will crash
with a `TemplateDoesNotExist` error.

## Examples

There are currently two themes included in DJ Press: `default` and `simple`. The `default` theme demonstrates how to
build a theme with just a single `index.html` file, whereas the `simple` theme uses all available template types.
