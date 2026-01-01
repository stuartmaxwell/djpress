"""Template tags for djpress."""

from django import template
from django.contrib.auth.models import User
from django.core.paginator import Page
from django.db import models
from django.template import Context
from django.urls import reverse
from django.utils.safestring import mark_safe

from djpress import url_utils
from djpress.conf import settings as djpress_settings
from djpress.exceptions import PageNotFoundError
from djpress.models import Category, Post, Tag
from djpress.plugins import registry
from djpress.plugins.hook_registry import DJ_FOOTER, DJ_HEADER
from djpress.templatetags import helpers
from djpress.utils import get_author_display_name

register = template.Library()


# Tags starting with `get_` are used to get data from the database.


@register.simple_tag
def get_site_title() -> str:
    """Return the site title.

    Returns:
        str: The site title.
    """
    return str(djpress_settings.SITE_TITLE)


@register.simple_tag
def get_site_description() -> str:
    """Return the site description.

    Returns:
        str: The site description.
    """
    return str(djpress_settings.SITE_DESCRIPTION)


@register.simple_tag
def get_theme_setting(name: str, default: str | float | None = None) -> str | float | None:
    """Return the value of a theme setting.

    Args:
        name: The name of the setting.
        default: The default value to return if the setting is not found.

    Returns:
        str: The value of the setting, or the default value if not found.
    """
    # Get the current theme
    current_theme = djpress_settings.THEME

    # Get the theme settings
    theme_settings = djpress_settings.THEME_SETTINGS.get(current_theme, {})

    # If there are no theme settings, return the default value
    if not theme_settings:
        return default

    # Return the value of the setting, or the default value if not found
    return theme_settings.get(name, default)


@register.simple_tag
def get_posts() -> models.QuerySet[Post]:
    """Return all published posts as a queryset.

    Returns:
        models.QuerySet[Post]: All posts.
    """
    return Post.post_objects.get_published_posts()


@register.simple_tag(takes_context=True)
def get_recent_posts(context: Context) -> models.QuerySet[Post]:
    """Return the recent posts.

    This returns the most recent published posts, and tries to be efficient by checking if there's a `posts` object we
    can use.
    """
    posts: Page | None = context.get("posts")

    if isinstance(posts, Page) and posts.number == 1:
        return posts.object_list

    return Post.post_objects.get_recent_published_posts()


@register.simple_tag
def get_pages() -> models.QuerySet[Post]:
    """Return all published pages as a queryset.

    Returns:
        models.QuerySet[Post]: All pages.
    """
    return Post.page_objects.get_published_pages()


@register.simple_tag
def get_categories() -> models.QuerySet[Category] | None:
    """Return all categories as a queryset.

    Returns:
        models.QuerySet[Category]: All categories.
    """
    return Category.objects.get_categories().order_by("menu_order", "title")


@register.simple_tag
def get_tags() -> models.QuerySet[Tag]:
    """Return all tags as a queryset.

    Returns:
        models.QuerySet[Tag]: All tags.
    """
    return Tag.objects.get_tags().order_by("title")


@register.simple_tag(takes_context=True)
def get_post_title(context: Context, *, include_empty: bool = False) -> str:
    """Return the title of a post.

    This is just the title of the post from the current context with no further HTML.

    If `include_empty` is set to `True`, then the title will be returned from the `post_title` property of the Post.

    Args:
        context: The context.
        include_empty: Whether to include the title if it is empty.

    Returns:
        str: The title of the post.
    """
    post: Post | None = context.get("post")
    if not post:
        return ""

    if include_empty:
        return post.post_title

    return post.title


@register.simple_tag(takes_context=True)
def get_post_url(context: Context) -> str:
    """Return the URL of a post.

    This is just the URL of the post from the current context with no further HTML.

    Args:
        context: The context.

    Returns:
        str: The URL of the post.
    """
    post: Post | None = context.get("post")
    if not post:
        return ""

    return post.url


@register.simple_tag(takes_context=True)
def get_post_author(context: Context) -> str:
    """Return the author display name.

    Tries to display the first name and last name if available, otherwise falls back to
    the username.

    Args:
        context: The context.

    Returns:
        str: The author display name.
    """
    post: Post | None = context.get("post")
    if not post:
        return ""

    author = post.author

    return get_author_display_name(author)


@register.simple_tag(takes_context=True)
def get_post_date(context: Context) -> str:
    """Return the date of a post.

    Args:
        context: The context.

    Returns:
        str: The date of the post.
    """
    post: Post | None = context.get("post")
    if not post:
        return ""

    output_date = post.local_datetime
    return output_date.strftime("%b %-d, %Y")


@register.simple_tag(takes_context=True)
def get_post_categories(context: Context) -> models.QuerySet[Category]:
    """Return a queryset of categories for the post.

    Returns:
        queryset: A queryset of categories.
    """
    post: Post | None = context.get("post")
    if not post:
        return Category.objects.none()

    return post.categories.all()


@register.simple_tag(takes_context=True)
def get_post_category_slugs(context: Context) -> list:
    """Return a list of category slugs for the post.

    Returns:
        list: The categories of the post or an empty list
    """
    post: Post | None = context.get("post")
    if post is None:
        return []

    categories = post.categories.all()

    return [category.slug for category in categories]


@register.simple_tag
def get_rss_url() -> str:
    """Return the URL to the RSS feed.

    Returns:
        str: The URL to the RSS feed.
    """
    return url_utils.get_rss_url()


@register.simple_tag
def get_search_url() -> str:
    """Return the search URL.

    Returns:
        str: The search URL path, or empty string if search is disabled.

    Example:
        <form action="{% search_url %}" method="get">
            <input type="search" name="q" placeholder="Search...">
            <button type="submit">Search</button>
        </form>
    """
    return url_utils.get_search_url()


@register.simple_tag(takes_context=True)
def get_pagination_range(context: Context) -> range:
    """Return the range of pagination pages.

    Args:
        context: The context.

    Returns:
        range: The pagination pages.
    """
    page: Page | None = context.get("posts")
    if not page or not isinstance(page, Page):
        return range(0)

    return page.paginator.page_range


@register.simple_tag(takes_context=True)
def get_pagination_current_page(context: Context) -> int:
    """Return the current page number.

    Args:
        context: The context.

    Returns:
        int: The current page number.
    """
    page: Page | None = context.get("posts")
    if not page or not isinstance(page, Page):
        return 0

    return page.number


"""
# Display Tags - Site-wide

These tags retrieve data about the site and format it with HTML, ready to be displayed in your templates.
"""


@register.simple_tag
def site_title(
    outer_tag: str = "",
    *,
    outer_class: str = "",
    link: bool = False,
    link_class: str = "",
) -> str:
    """Return the site title as safely marked HTML.

    This must be called with named arguments, except the outer_tag. For example, the following two statements are
    identical:

    - `{% site_title "h1" %}`
    - `{% site_title outer_tag="h1" %}`

    Args:
        outer_tag: The HTML tag to wrap the title in.
        outer_class: The CSS class(es) for the outer tag.
        link: Whether to wrap the title in a link.
        link_class: The CSS class(es) for the link.

    Returns:
        str: Safely-marked HTML with the site title.
    """
    site_title = str(djpress_settings.SITE_TITLE)
    if site_title == "":
        return ""

    link_class_html = f' class="{link_class}"' if link_class else ""

    link_html = f'<a href="{reverse("djpress:index")}"{link_class_html}>{site_title}</a>' if link else site_title

    if outer_tag == "":
        return link_html

    # If outer_tag is not one of the allowed tags, return an empty string.
    # TODO: move these tags to a constant?
    if outer_tag not in ["p", "div", "span", "article", "h1", "h2", "h3", "h4", "h5", "h6"]:
        return ""

    outer_class_html = f' class="{outer_class}"' if outer_class else ""

    output = f"<{outer_tag}{outer_class_html}>{link_html}</{outer_tag}>"

    return mark_safe(output)


@register.simple_tag
def site_description(
    outer_tag: str = "",
    *,
    outer_class: str = "",
) -> str:
    """Return the site description as safely marked HTML.

    This must be called with named arguments.

    Args:
        outer_tag: The HTML tag to wrap the description in.
        outer_class: The CSS class(es) for the outer tag.

    Returns:
        str: The site description as safely marked HTML.
    """
    site_description = str(djpress_settings.SITE_DESCRIPTION)
    if site_description == "":
        return ""

    if outer_tag == "":
        return site_description

    # If outer_tag is not one of the allowed tags, return an empty string.
    # TODO: move these tags to a constant?
    if outer_tag not in ["p", "div", "span", "article", "h1", "h2", "h3", "h4", "h5", "h6"]:
        return ""

    outer_class_html = f' class="{outer_class}"' if outer_class else ""

    output = f"<{outer_tag}{outer_class_html}>{site_description}</{outer_tag}>"

    return mark_safe(output)


@register.simple_tag(takes_context=True)
def page_title(
    context: Context,
    pre_text: str = "",
    post_text: str = "",
) -> str:
    """Return the page title.

    Args:
        context: The context.
        pre_text: The text to prepend to the page title.
        post_text: The text to append to the page title.

    Returns:
        str: The page title.
    """
    category: Category | None = context.get("category")
    author: User | None = context.get("author")
    post: Post | None = context.get("post")

    if category:
        title = category.title

    elif author:
        title = get_author_display_name(author)

    elif post:
        title = post.title
    else:
        title = ""

    if title:
        title = f"{pre_text}{title}{post_text}"

    return title


@register.simple_tag
def site_categories(
    outer_tag: str = "ul",
    *,
    outer_class: str = "",
    link_class: str = "",
    separator: str = ", ",
    pre_text: str = "",
    post_text: str = "",
) -> str:
    """Return the categories of the blog.

    Args:
        outer_tag: The outer HTML tag for the categories.
        outer_class: The CSS class(es) for the outer tag.
        link_class: The CSS class(es) for the link.
        separator: The separator between categories.
        pre_text: The text to prepend to the categories.
        post_text: The text to append to the categories.

    Returns:
        str: The categories of the blog.
    """
    categories = Category.objects.all()
    if not categories:
        return ""

    return mark_safe(
        helpers.categories_html(
            categories=categories,
            outer_tag=outer_tag,
            outer_class=outer_class,
            link_class=link_class,
            separator=separator,
            pre_text=pre_text,
            post_text=post_text,
        ),
    )


@register.simple_tag
def site_tags(
    outer_tag: str = "ul",
    *,
    outer_class: str = "",
    link_class: str = "",
    separator: str = ", ",
    pre_text: str = "",
    post_text: str = "",
) -> str:
    """Return the tags of the blog.

    Args:
        outer_tag: The outer HTML tag for the tags.
        outer_class: The CSS class(es) for the outer tag.
        link_class: The CSS class(es) for the link.
        separator: The separator between tags.
        pre_text: The text to prepend to the tags.
        post_text: The text to append to the tags.

    Returns:
        str: The tags of the blog.
    """
    tags = Tag.objects.get_tags().order_by("title")
    if not tags:
        return ""

    return mark_safe(
        helpers.tags_html(
            tags=tags,
            outer_tag=outer_tag,
            outer_class=outer_class,
            link_class=link_class,
            separator=separator,
            pre_text=pre_text,
            post_text=post_text,
        )
    )


@register.simple_tag
def tags_with_counts(
    outer_tag: str = "ul",
    *,
    outer_class: str = "",
    link_class: str = "",
) -> str:
    """Return the tags of the blog with post counts.

    Each tag shows the tag name followed by the number of posts in parentheses.
    Only tags that have published posts are included.

    Args:
        outer_tag: The outer HTML tag for the tags: "ul", "div", or "span".
        outer_class: The CSS class(es) for the outer tag.
        link_class: The CSS class(es) for the link.

    Returns:
        str: The tags of the blog with post counts.
    """
    tags = Tag.objects.get_tags_with_published_posts().order_by("title")

    if not tags:
        return ""

    # If outer_tag is not one of the allowed tags, return an empty string.
    if outer_tag not in ["ul", "div", "span"]:
        return ""

    output = ""
    outer_class_html = f' class="{outer_class}"' if outer_class else ""

    if outer_tag == "ul":
        output += f"<ul{outer_class_html}>"
        for tag in tags:
            count = tag.posts.count()
            output += f"<li>{helpers.tag_link(tag, link_class)} ({count})</li>"
        output += "</ul>"

    if outer_tag == "div":
        output += f"<div{outer_class_html}>"
        for tag in tags:
            count = tag.posts.count()
            output += f"{helpers.tag_link(tag, link_class)} ({count}), "
        output = output[:-2]  # Remove the trailing comma and space
        output += "</div>"

    if outer_tag == "span":
        output += f"<span{outer_class_html}>"
        for tag in tags:
            count = tag.posts.count()
            output += f"{helpers.tag_link(tag, link_class)} ({count}), "
        output = output[:-2]  # Remove the trailing comma and space
        output += "</span>"

    return mark_safe(output)


@register.simple_tag
def site_pages(
    outer_tag: str = "div",
    *,
    outer_class: str = "",
    link_class: str = "",
    separator: str = ", ",
) -> str:
    """Return the pages of the site.

    This is used to generate a comma-separated list of linked pages with a separator between them, and wrapped in either
    a `div` or `span` tag. To get an HTML list of pages, use the `site_pages_list` tag.

    Args:
        outer_tag: The outer HTML tag for the pages.
        outer_class: The CSS class(es) for the outer tag.
        link_class: The CSS class(es) for the link.
        separator: The separator between the pages.

    Returns:
        str: The pages of the site as safely marked HTML.
    """
    pages = Post.page_objects.get_published_pages()

    if not pages:
        return ""

    allowed_tags = ["div", "span"]
    if outer_tag not in allowed_tags:
        return ""

    outer_class_html = f' class="{outer_class}"' if outer_class else ""

    output = f"<{outer_tag}{outer_class_html}>"
    for page in pages:
        output += f"{helpers.get_page_link(page=page, link_class=link_class)}{separator}"
    output = output[: -len(separator)]  # Remove the trailing separator
    output += f"</{outer_tag}>"

    return mark_safe(output)


@register.simple_tag
def site_pages_list(
    *,
    ul_outer_class: str = "",
    li_class: str = "",
    a_class: str = "",
    ul_child_class: str = "",
    include_home: bool = False,
    levels: int = 0,
) -> str:
    """Returns an HTML list of the site's pages.

    The pages are sorted by menu order and then by title. Pages that have children have a nested list of children.

    The default output with no arguments is an unordered list with no classes. CSS classes can be added to the output by
    specifying the arguments shown below.

    ```
    <ul class="ul_outer_class">
        <li class="li_class">
            <a href="/page1/" class="a_class">Page 1</a>
        </li>
        <li class="li_class">
            <a href="/page2/" class="a_class">Page 2</a>
        </li>
        <li class="li_parent_class">
            <a href="/page3/" class="a_class">Page 3</a>
            <ul class="ul_child_class">
                <li class="li_class">
                    <a href="/page3/child1/" class="a_class">Child 1</a>
                </li>
                <li class="li_class">
                    <a href="/page3/child2/" class="a_class">Child 2</a>
                </li>
            </ul>
        </li>
    </ul>
    ```

    Args:
        ul_outer_class (str): The CSS class(es) for the outer unordered list.
        li_class (str): The CSS class(es) for the
        a_class (str): The CSS class(es) for the anchor tags.
        ul_child_class (str): The CSS class(es) for the nested unordered lists.
        include_home (bool): Whether to include the home page in the list.
        levels (int): The maximum depth of nested pages to include or 0 for unlimited.

    Returns:
        str: The HTML list of the blog pages.
    """
    pages = Post.page_objects.get_page_tree()

    output = ""

    if not pages and not include_home:
        return output

    if ul_outer_class:
        ul_outer_class = f' class="{ul_outer_class}"'

    output += f"<ul{ul_outer_class}>"

    if include_home:
        class_li = f' class="{li_class}"' if li_class else ""
        class_a = f' class="{a_class}"' if a_class else ""
        output += f'<li{class_li}><a href="{reverse("djpress:index")}"{class_a}>Home</a></li>'

    output += helpers.get_site_pages_list(
        pages, li_class=li_class, a_class=a_class, ul_child_class=ul_child_class, levels=levels
    )
    output += "</ul>"

    return mark_safe(output)


"""
# Post Content Tags

These tags help you display the content of posts. They only work if there is a `post` object in the context.
"""


@register.simple_tag(takes_context=True)
def post_title(
    context: Context,
    outer_tag: str = "",
    *,
    outer_class: str = "",
    link_class: str = "",
    force_link: bool = False,
    include_empty: bool = False,
) -> str:
    """Return the title link for a post.

    If the post is part of a posts collection, then return the title and a link to the post. If the post is a single
    post, then return just the title of the post with no link. But this behavior can be overridden by setting
    `force_link` to `True`.

    The outer tag can be any of the following: "h1", "h2", "h3", "h4", "h5", "h6", "p", "div", "span". If the outer_tag
    option is ommitted, then the title will be returned with no outer tag. If an invalid outer_tag is provided, an empty
    string will be returned.

    If the outer tag is one of the allowed tags, and if Microformats are enabled, then the outer tag will have the class
    "p-name".

    If the post doesn't have a title, return an empty string, but if `include_empty` is set to `True`, then the title
    will be returned from the `post_title` property of the Post.


    Otherwise return an empty string.

    Args:
        context: The context.
        outer_tag: The outer HTML tag for the title.
        outer_class: The CSS class(es) for the outer tag.
        link_class: The CSS class(es) for the link.
        force_link: Whether to force the link to be displayed.
        include_empty: Whether to include the title if it is empty.

    Returns:
        str: The title link for the post.
    """
    post: Post | None = context.get("post")
    posts: Page | None = context.get("posts")

    # If there's no post in the context, return an empty string.
    if not post:
        return ""

    # If there's no title, return an empty string.
    if not post.title and not include_empty:
        return ""

    # Get the title of the post
    output = post.post_title if include_empty else post.title

    # If there's a posts in the context, or if the link is forced, then we need to display the link.
    if posts or force_link:
        # If Microformats are enabled, include the u-url class.
        mf_link = "u-url" if djpress_settings.MICROFORMATS_ENABLED else ""

        link_classes = f"{mf_link} {link_class}".strip()
        link_class_html = f' class="{link_classes}"' if link_classes else ""

        output = f'<a href="{post.url}" title="{output}"{link_class_html}>{output}</a>'

    # If there's no outer tag, return the output as is
    if outer_tag == "":
        return mark_safe(output)

    # If the outer tag is one of the allowed tags, then wrap the output in the outer tag.
    if outer_tag not in ["h1", "h2", "h3", "h4", "h5", "h6", "p", "div", "span"]:
        return ""

    # If Microformats are enabled, use p-name with the outer tag.
    mf = "p-name" if djpress_settings.MICROFORMATS_ENABLED else ""

    outer_classes = f"{mf} {outer_class}".strip()
    outer_class_html = f' class="{outer_classes}"' if outer_classes else ""

    output = f"<{outer_tag}{outer_class_html}>{output}</{outer_tag}>"

    return mark_safe(output)


@register.simple_tag(takes_context=True)
def post_content(
    context: Context,
    outer_tag: str = "",
    *,
    outer_class: str = "",
    read_more_link_class: str = "",
    read_more_text: str = "",
) -> str:
    """Return the content of a post.

    If the post is part of a posts collection, then we return the truncated content of
    the post with the read more link.

    If the post is a single post, return the full content of the post.

    The outer tag can be any one of the following: "section", "div", "article", "p", "span". If the outer tag is not one
    of these, then the content will be returned with no outer tag.

    If there's an outer tag, and if microformats are enabled, then the outer tag will have the class "e-content".

    If there's no post, return an empty string.

    Args:
        context: The context.
        outer_tag: The outer HTML tag for the content.
        outer_class: The CSS class(es) for the outer tag.
        read_more_link_class: The CSS class(es) for the read more link.
        read_more_text: The text for the read more link.

    Returns:
        str: The content of the post.
    """
    # Check if there's a post or posts in the context.
    post: Post | None = context.get("post")
    posts: Page | None = context.get("posts")

    # If there's no post, return an empty string.
    if not post:
        return ""

    # If there's a posts in the context, then we need to display the truncated content.
    # Note: the read more link will return an empty string if the post is not truncated.
    if posts:
        content = post.truncated_content_markdown + helpers.post_read_more_link(
            post, read_more_link_class, read_more_text
        )
    else:
        content = post.content_markdown

    # If the outer tag is one of the allowed tags, then wrap the output in the outer tag.
    if outer_tag in ["section", "div", "article", "p", "span"]:
        # If Microformats are enabled, use e-content with the outer tag.
        mf = "e-content" if djpress_settings.MICROFORMATS_ENABLED else ""

        outer_classes = f"{mf} {outer_class}".strip()
        outer_class_html = f' class="{outer_classes}"' if outer_classes else ""

        content = f"<{outer_tag}{outer_class_html}>{content}</{outer_tag}>"

    return mark_safe(content)


@register.simple_tag(takes_context=True)
def post_date(
    context: Context,
    link_class: str = "",
) -> str:
    """Return the date link for a post.

    Args:
        context: The context.
        link_class: The CSS class(es) for the link.

    Returns:
        str: The date link for the post.
    """
    post: Post | None = context.get("post")
    if not post:
        return ""
    output_date = post.local_datetime

    if not djpress_settings.ARCHIVE_ENABLED:
        return mark_safe(output_date.strftime("%b %-d, %Y"))

    post_year = output_date.strftime("%Y")
    post_month = output_date.strftime("%m")
    post_month_name = output_date.strftime("%b")
    post_day = output_date.strftime("%d")
    post_day_name = output_date.strftime("%-d")
    post_time = output_date.strftime("%-I:%M %p")

    year_url = url_utils.get_archives_url(year=int(post_year))
    month_url = url_utils.get_archives_url(year=int(post_year), month=int(post_month))
    day_url = url_utils.get_archives_url(year=int(post_year), month=int(post_month), day=int(post_day))

    link_class_html = f' class="{link_class}"' if link_class else ""

    output = (
        f'<a href="{month_url}" title="View all posts in {post_month_name} {post_year}"'
        f"{link_class_html}>{post_month_name}</a> "
        f'<a href="{day_url}" title="View all posts on {post_day_name} '
        f'{post_month_name} {post_year}"{link_class_html}>{post_day_name}</a>, '
        f'<a href="{year_url}" title="View all posts in {post_year}"{link_class_html}>'
        f"{post_year}</a>, "
        f"{post_time}."
    )

    # If Microformats are enabled, use dt-published with the date.
    if djpress_settings.MICROFORMATS_ENABLED:
        output = f'<time class="dt-published" datetime="{output_date.isoformat()}">{output}</time>'

    return mark_safe(output)


@register.simple_tag(takes_context=True)
def post_author(
    context: Context,
    outer_tag: str = "span",
    *,
    outer_class: str = "",
    link_class: str = "",
    pre_text: str = "",
    post_text: str = "",
) -> str:
    """Return the author link for a post.

    Args:
        context: The context.
        outer_tag: The outer tag for the author display name.
        outer_class: The CSS class(es) for the outer tag.
        link_class: The CSS class(es) for the link.
        pre_text: The text to display before the author name.
        post_text: The text to display after the author name.

    Returns:
        str: The author link.
    """
    post: Post | None = context.get("post")
    if not post:
        return ""

    # If the outer tag is one of the allowed tags, then wrap the output in the outer tag.
    allowed_tags = ["h1", "h2", "h3", "h4", "h5", "h6", "p", "div", "span"]
    if outer_tag not in allowed_tags:
        return ""

    # Add p-category if microformats are enabled
    mf = "p-author" if djpress_settings.MICROFORMATS_ENABLED else ""

    outer_classes = f"{mf} {outer_class}".strip()
    outer_class_html = f' class="{outer_classes}"' if outer_classes else ""

    link_class_html = f' class="{link_class}"' if link_class else ""

    author = post.author
    author_display_name = get_author_display_name(author)

    if not djpress_settings.AUTHOR_ENABLED:
        return f"<{outer_tag}{outer_class_html}>{pre_text}{author_display_name}{post_text}</{outer_tag}>"

    author_url = url_utils.get_author_url(user=author)

    output = (
        f"<{outer_tag}{outer_class_html}>{pre_text}"
        f'<a href="{author_url}" title="View all posts by {author_display_name}"{link_class_html}>'
        f"{author_display_name}</a>{post_text}</{outer_tag}>"
    )

    return mark_safe(output)


@register.simple_tag(takes_context=True)
def post_categories(
    context: Context,
    outer_tag: str = "ul",
    *,
    outer_class: str = "",
    link_class: str = "",
    separator: str = ", ",
    pre_text: str = "",
    post_text: str = "",
) -> str:
    """Return the categories of a post.

    Each category is a link to the category page.

    Args:
        context: The context.
        outer_tag: The outer HTML tag for the categories.
        outer_class: The CSS class(es) for the outer tag.
        link_class: The CSS class(es) for the link.
        separator: The separator between categories.
        pre_text: The text to display before the categories.
        post_text: The text to display after the categories.

    Returns:
        str: The categories of the post.
    """
    post: Post | None = context.get("post")
    if not post:
        return ""

    categories = post.categories.all()
    if not categories:
        return ""

    # Explicitly pass outer_tag parameter for clarity
    return mark_safe(
        helpers.categories_html(
            categories=categories,
            outer_tag=outer_tag,
            outer_class=outer_class,
            link_class=link_class,
            separator=separator,
            pre_text=pre_text,
            post_text=post_text,
        ),
    )


@register.simple_tag(takes_context=True)
def post_tags(
    context: Context,
    outer_tag: str = "ul",
    *,
    outer_class: str = "",
    link_class: str = "",
    separator: str = ", ",
    pre_text: str = "",
    post_text: str = "",
) -> str:
    """Return the tags of a post.

    Each tag is a link to the tag page.

    Args:
        context: The context.
        outer_tag: The outer HTML tag for the tags.
        outer_class: The CSS class(es) for the outer tag.
        link_class: The CSS class(es) for the link.
        separator: The separator between tags.
        pre_text: The text to display before the tags.
        post_text: The text to display after the tags.

    Returns:
        str: The tags of the post.
    """
    post: Post | None = context.get("post")
    if not post:
        return ""

    tags = post.tags.all()
    if not tags:
        return ""

    allowed_outer_tags = ["ul", "div", "span"]
    if outer_tag not in allowed_outer_tags:
        return ""

    # Explicitly pass outer_tag parameter for clarity
    return mark_safe(
        helpers.tags_html(
            tags=tags,
            outer_tag=outer_tag,
            outer_class=outer_class,
            link_class=link_class,
            separator=separator,
            pre_text=pre_text,
            post_text=post_text,
        )
    )


"""
# Search Tags

These tags provide search functionality for your blog.
"""


@register.simple_tag(takes_context=True)
def search_form(
    context: Context,
    *,
    placeholder: str = "Search...",
    button_text: str = "Search",
    form_class: str = "",
    input_class: str = "",
    button_class: str = "",
    show_button: bool = True,
) -> str:
    """Return a search form as HTML.

    For a custom search form, use the {% search_url %} tag instead.

    Args:
        context: The template context - this is added automatically by Django.
        placeholder: Placeholder text for the search input.
        button_text: Text for the submit button.
        form_class: CSS class(es) for the form element.
        input_class: CSS class(es) for the input element.
        button_class: CSS class(es) for the button element.
        show_button: Whether to show the submit button.

    Returns:
        str: The search form HTML, or empty string if search is disabled.

    Example:
        {% search_form %}
        {% search_form placeholder="Search posts..." button_text="Go" form_class="my-form" %}
    """
    url = url_utils.get_search_url()

    if not url:
        return ""

    current_query = context.get("search_query", "")

    # Build the HTML
    form_class_attr = f' class="{form_class}"' if form_class else ""
    input_class_attr = f' class="{input_class}"' if input_class else ""
    button_class_attr = f' class="{button_class}"' if button_class else ""

    html = f'<form action="{url}" method="get"{form_class_attr}>'
    html += '<input type="search" name="q" '
    html += f'value="{current_query}" placeholder="{placeholder}" aria-label="Search"{input_class_attr}>'

    if show_button:
        html += f'<button type="submit"{button_class_attr}>{button_text}</button>'

    html += "</form>"

    return mark_safe(html)


@register.simple_tag(takes_context=True)
def search_errors(
    context: Context,
    outer_tag: str = "div",
    *,
    outer_class: str = "search-errors",
    error_tag: str = "p",
    error_class: str = "error",
) -> str:
    """Return search validation errors as HTML.

    Expects there to be a `search_errors` list in the context. If there are no errors,
    returns an empty string.

    Args:
        context: The template context.
        outer_tag: The outer HTML tag to wrap all errors (div, section, etc).
        outer_class: The CSS class(es) for the outer tag.
        error_tag: The HTML tag for each individual error message.
        error_class: The CSS class(es) for each error tag.

    Returns:
        str: The error messages HTML, or empty string if no errors.

    Example:
        {% search_errors %}
        {% search_errors outer="section" outer_class="alert alert-danger" %}
    """
    errors: list | None = context.get("search_errors")

    if not errors or not isinstance(errors, list):
        return ""

    allowed_outer_tags = ["div", "section", "aside", "article"]
    allowed_error_tags = ["p", "span", "div", "li"]

    if outer_tag not in allowed_outer_tags:
        return ""

    if error_tag not in allowed_error_tags:
        return ""

    outer_class_html = f' class="{outer_class}"' if outer_class else ""
    error_class_html = f' class="{error_class}"' if error_class else ""

    html = f"<{outer_tag}{outer_class_html}>"

    for error in errors:
        if isinstance(error, str):
            html += f"<{error_tag}{error_class_html}>{error}</{error_tag}>"

    html += f"</{outer_tag}>"

    return mark_safe(html)


"""
# Utility Tags

These tags provide additional helper functions for your templates.
"""


@register.simple_tag(takes_context=True)
def category_title(
    context: Context,
    outer_tag: str = "",
    *,
    outer_class: str = "",
    pre_text: str = "",
    post_text: str = "",
) -> str:
    """Return the title of a category.

    Expects there to be an `category` in the context set to a Category object. If there's no category in the context or
    category is not a Category object, then return an empty string.


    Args:
        context: The context.
        outer_tag: The outer HTML tag for the category.
        outer_class: The CSS class(es) for the outer tag.
        pre_text: The text to prepend to the category title.
        post_text: The text to append to the category title.

    Returns:
        str: The title of the category formatted with the outer tag and class if provided.
    """
    category: Category | None = context.get("category")

    if not category or not isinstance(category, Category):
        return ""

    outer_class = f' class="{outer_class}"' if outer_class else ""

    output = category.title

    if pre_text:
        output = f"{pre_text}{output}"

    if post_text:
        output = f"{output}{post_text}"

    if outer_tag == "":
        return output

    allowed_outer_tags = ["h1", "h2", "h3", "h4", "h5", "h6", "p", "div", "span"]
    if outer_tag not in allowed_outer_tags:
        return ""

    return mark_safe(f"<{outer_tag}{outer_class}>{output}</{outer_tag}>")

    return output


@register.simple_tag(takes_context=True)
def tag_title(
    context: Context,
    outer_tag: str = "",
    *,
    outer_class: str = "",
    pre_text: str = "",
    post_text: str = "",
    separator: str = ", ",
) -> str:
    """Return the title of the current tag.

    Expects there to be 'tags' in the context set to a list of tag slugs. In the tag views,
    this will show the tag or tags being displayed. If there's no tags in the context,
    returns an empty string.

    Args:
        context: The context.
        outer_tag: The outer HTML tag for the tag title.
        outer_class: The CSS class(es) for the outer tag.
        pre_text: The text to prepend to the tag title.
        post_text: The text to append to the tag title.
        separator: The separator between tag titles.

    Returns:
        str: The title of the tag formatted with the outer tag and class if
        provided.
    """
    tag_slugs: list | None = context.get("tags")

    if not tag_slugs:
        return ""

    # Get tag titles from the slugs
    tags = [Tag.objects.get_tag_by_slug(slug) for slug in tag_slugs]
    tag_titles = [tag.title for tag in tags]

    # Join multiple tags with commas
    output = separator.join(tag_titles) if len(tag_titles) > 1 else tag_titles[0]

    if pre_text:
        output = f"{pre_text}{output}"

    if post_text:
        output = f"{output}{post_text}"

    if outer_tag == "":
        return output

    allowed_outer_tags = ["h1", "h2", "h3", "h4", "h5", "h6", "p", "div", "span"]
    if outer_tag not in allowed_outer_tags:
        return ""

    outer_class_html = f' class="{outer_class}"' if outer_class else ""

    return mark_safe(f"<{outer_tag}{outer_class_html}>{output}</{outer_tag}>")

    return output


@register.simple_tag(takes_context=True)
def search_title(
    context: Context,
    outer_tag: str = "",
    *,
    outer_class: str = "",
    pre_text: str = "",
    post_text: str = "",
) -> str:
    """Return the title of a search query.

    Expects there to be an `search_query` in the context set to a string. If there's no search_query in the context or
    search_query is not a string, then return an empty string.


    Args:
        context: The context.
        outer_tag: The outer HTML tag for the category.
        outer_class: The CSS class(es) for the outer tag.
        pre_text: The text to prepend to the category title.
        post_text: The text to append to the category title.

    Returns:
        str: The title of the search query formatted with the outer tag and class if provided.
    """
    search_query: str | None = context.get("search_query")

    if not search_query or not isinstance(search_query, str):
        return ""

    output = search_query

    if pre_text:
        output = f"{pre_text}{output}"

    if post_text:
        output = f"{output}{post_text}"

    if outer_tag == "":
        return mark_safe(output)

    allowed_outer_tags = ["h1", "h2", "h3", "h4", "h5", "h6", "p", "div", "span"]
    if outer_tag not in allowed_outer_tags:
        return ""

    outer_class = f' class="{outer_class}"' if outer_class else ""

    return mark_safe(f"<{outer_tag}{outer_class}>{output}</{outer_tag}>")


@register.simple_tag(takes_context=True)
def author_name(
    context: Context,
    outer_tag: str = "",
    *,
    outer_class: str = "",
    pre_text: str = "",
    post_text: str = "",
) -> str:
    """Return the name of an author.

    Expects there to be an `author` in the context set to a user object. If there's no
    author in the context or author is not a User object, then return an empty string.

    Args:
        context: The context.
        outer_tag: The outer HTML tag for the author.
        outer_class: The CSS class(es) for the outer tag.
        pre_text: The text to prepend to the author name.
        post_text: The text to append to the author name.

    Returns:
        str: The name of the author formatted with the outer tag and class if
        provided.
    """
    author: User | None = context.get("author")

    if not author or not isinstance(author, User):
        return ""

    output = get_author_display_name(author)

    if pre_text:
        output = f"{pre_text}{output}"

    if post_text:
        output = f"{output}{post_text}"

    if outer_tag == "":
        return mark_safe(output)

    allowed_outer_tags = ["h1", "h2", "h3", "h4", "h5", "h6", "p", "div", "span"]
    if outer_tag not in allowed_outer_tags:
        return ""

    outer_class = f' class="{outer_class}"' if outer_class else ""

    return mark_safe(f"<{outer_tag}{outer_class}>{output}</{outer_tag}>")


@register.simple_tag(takes_context=True)
def is_paginated(
    context: Context,
) -> bool:
    """Return whether the posts are paginated.

    Args:
        context: The context.

    Returns:
        bool: Whether the posts are paginated.
    """
    posts: Page | None = context.get("posts")
    if not posts or not isinstance(posts, Page):  # noqa: SIM103
        return False

    return True


@register.simple_tag(takes_context=True)
def pagination_links(
    context: Context,
) -> str:
    """Return the previous and next post links.

    This checks if there is a Page object in the context. If there is, then we return
    the previous and next post links. If there is no Page object in the context, then
    we return an empty string.

    Args:
        context: The context.

    Returns:
        str: The previous and next post links.
    """
    page: Page | None = context.get("posts")
    if not page or not isinstance(page, Page):
        return ""

    # Get the request to preserve query string parameters
    request = context.get("request")

    def build_pagination_url(page_number: int) -> str:
        """Build URL with preserved query string parameters."""
        if request and hasattr(request, "GET"):
            params = request.GET.copy()
            params["page"] = page_number
            return f"?{params.urlencode()}"
        return f"?page={page_number}"

    if page.has_previous():
        previous_output = (
            f'<span class="previous">'
            f'<a href="{build_pagination_url(1)}">&laquo; first</a> '
            f'<a href="{build_pagination_url(page.previous_page_number())}">previous</a>'
            f"</span>"
        )
    else:
        previous_output = ""

    if page.has_next():
        next_output = (
            f'<span class="next">'
            f'<a href="{build_pagination_url(page.next_page_number())}">next</a> '
            f'<a href="{build_pagination_url(page.paginator.num_pages)}">last &raquo;</a>'
            f"</span>"
        )
    else:
        next_output = ""

    current_output = f'<span class="current">Page {page.number} of {page.paginator.num_pages}</span>'

    return mark_safe(
        f'<div class="pagination">{previous_output} {current_output} {next_output}</div>',
    )


@register.simple_tag()
def page_link(
    page_slug: str,
    *,
    outer_tag: str = "",
    outer_class: str = "",
    link_class: str = "",
) -> str:
    """Return the link to a page.

    Args:
        page_slug: The slug of the page.
        outer_tag: The outer HTML tag for the page link.
        outer_class: The CSS class(es) for the outer tag.
        link_class: The CSS class(es) for the link.

    Returns:
        str: The link to the page.
    """
    try:
        page: Post | None = Post.page_objects.get_published_page_by_slug(page_slug)
    except PageNotFoundError:
        return ""

    output = helpers.get_page_link(page, link_class=link_class)

    if outer_tag == "":
        return mark_safe(output)

    allowed_tags = ["h1", "h2", "h3", "h4", "h5", "h6", "div", "span", "li"]
    if outer_tag not in allowed_tags:
        return ""

    outer_class_html = f' class="{outer_class}"' if outer_class else ""

    return mark_safe(f"<{outer_tag}{outer_class_html}>{output}</{outer_tag}>")


@register.simple_tag
def rss_link() -> str:
    """Return an HTML link to the RSS feed.

    If the RSS feed is enabled, then return an HTML link tag that points to the RSS feed. Otherwise, return an empty
    string.

    Example:
        ```django
        {% rss_link %}
        ```

        ```html
        <link rel="alternate" type="application/rss+xml" title="Latest Posts" href="/rss/">
        ```

    Returns:
        str: The HTML link to the RSS feed.
    """
    if not djpress_settings.RSS_ENABLED:
        return ""

    rss_url = url_utils.get_rss_url()

    return mark_safe(f'<link rel="alternate" type="application/rss+xml" title="Latest Posts" href="{rss_url}">')


@register.tag(name="post_wrap")
def post_wrapper_tag(
    parser: template.base.Parser,
    token: template.base.Token,
) -> helpers.BlogPostWrapper:
    """Parse the blog post wrapper tag.

    This is a template tag that wraps the blog post content in a configurable HTML tag with a CSS class.

    Example usage:
        {% post_wrap "article" "post" %}<p>Post content</p>{% end_post_wrap %}

    Args:
        parser: The template parser.
        token: The template token.

    Returns:
        BlogPostWrapper: The blog post wrapper tag.
    """
    params = token.split_contents()[1:]  # skip the tag name

    tag, css_class = helpers.parse_post_wrapper_params(params)

    # If microformats are enabled, add the h-entry class before the css class
    if djpress_settings.MICROFORMATS_ENABLED:
        css_class = f"h-entry {css_class}" if css_class else "h-entry"

    if css_class:
        css_class = f' class="{css_class}"'

    nodelist = parser.parse(("end_post_wrap",))
    parser.delete_first_token()

    return helpers.BlogPostWrapper(nodelist, tag, css_class)


# Plugin hook template tags


@register.simple_tag()
def djpress_header() -> str:
    """Return HTML content from plugins registered to the dj_header hook.

    This allows plugins to inject HTML content into the <head> section of templates.
    Plugins can register callbacks for the DJ_HEADER hook to add meta tags, styles,
    scripts, or other head content.

    Returns:
        str: HTML content from all registered dj_header hook callbacks, marked as safe.
    """
    content = registry.run_hook(DJ_HEADER)
    return mark_safe(content or "")


@register.simple_tag()
def djpress_footer() -> str:
    """Return HTML content from plugins registered to the dj_footer hook.

    This allows plugins to inject HTML content near the end of HTML documents,
    typically before the closing </body> tag or within <footer> elements.
    Plugins can register callbacks for the DJ_FOOTER hook to add analytics,
    scripts, or other footer content.

    Returns:
        str: HTML content from all registered dj_footer hook callbacks, marked as safe.
    """
    content = registry.run_hook(DJ_FOOTER)
    return mark_safe(content or "")
