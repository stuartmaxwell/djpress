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
from djpress.models import Category, Post
from djpress.templatetags import helpers
from djpress.utils import get_author_display_name

register = template.Library()


# Tags starting with `get_` are used to get data from the database.


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
def get_posts() -> models.QuerySet[Post]:
    """Return all published posts as a queryset.

    Returns:
        models.QuerySet[Post]: All posts.
    """
    return Post.post_objects.get_published_posts()


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
def blog_title() -> str:
    """Return the blog title.

    Returns:
        str: The blog title.
    """
    return djpress_settings.BLOG_TITLE


@register.simple_tag
def blog_title_link(link_class: str = "") -> str:
    """Return the blog title.

    Args:
        link_class: The CSS class(es) for the link.

    Returns:
        str: The blog title.
    """
    link_class_html = f' class="{link_class}"' if link_class else ""

    output = f'<a href="{reverse("djpress:index")}"{link_class_html}>{djpress_settings.BLOG_TITLE}</a>'

    return mark_safe(output)


@register.simple_tag
def blog_categories(
    outer: str = "ul",
    outer_class: str = "",
    link_class: str = "",
) -> str:
    """Return the categories of the blog.

    Args:
        outer: The outer HTML tag for the categories.
        outer_class: The CSS class(es) for the outer tag.
        link_class: The CSS class(es) for the link.

    Returns:
        str: The categories of the blog.
    """
    categories = Category.objects.all()
    if not categories:
        return ""

    return mark_safe(helpers.categories_html(categories, outer, outer_class, link_class))


@register.simple_tag
def blog_pages_list(ul_outer_class: str = "", li_class: str = "", a_class: str = "", ul_child_class: str = "") -> str:
    """Returns an HTML list of the blog pages.

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

    Returns:
        str: The HTML list of the blog pages.
    """
    pages = Post.page_objects.get_page_tree()

    output = ""

    if not pages:
        return output

    if ul_outer_class:
        ul_outer_class = f' class="{ul_outer_class}"'

    output += f"<ul{ul_outer_class}>"
    output += helpers.get_blog_pages_list(pages, li_class=li_class, a_class=a_class, ul_child_class=ul_child_class)
    output += "</ul>"

    return mark_safe(output)


@register.simple_tag
def blog_pages(
    outer: str = "ul",
    outer_class: str = "",
    link_class: str = "",
) -> str:
    """Return the pages of the blog.

    Args:
        outer: The outer HTML tag for the pages.
        outer_class: The CSS class(es) for the outer tag.
        link_class: The CSS class(es) for the link.

    Returns:
        str: The pages of the blog.
    """
    pages: models.QuerySet[Post] = get_pages()

    if not pages:
        return ""

    output = ""

    outer_class_html = f' class="{outer_class}"' if outer_class else ""

    if outer == "ul":
        output += f"<ul{outer_class_html}>"
        for page in pages:
            output += f"<li>{helpers.get_page_link(page=page, link_class=link_class)}</li>"
        output += "</ul>"

    if outer == "div":
        output += f"<div{outer_class_html}>"
        for page in pages:
            output += f"{helpers.get_page_link(page=page, link_class=link_class)}, "
        output = output[:-2]  # Remove the trailing comma and space
        output += "</div>"

    if outer == "span":
        output += f"<span{outer_class_html}>"
        for page in pages:
            output += f"{helpers.get_page_link(page=page, link_class=link_class)}, "
        output = output[:-2]  # Remove the trailing comma and space
        output += "</span>"

    return mark_safe(output)


@register.simple_tag(takes_context=True)
def blog_page_title(
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
        page_title = category.title

    elif author:
        page_title = get_author_display_name(author)

    elif post:
        page_title = post.title
    else:
        page_title = ""

    if page_title:
        page_title = f"{pre_text}{page_title}{post_text}"

    return page_title


@register.simple_tag(takes_context=True)
def have_posts(context: Context) -> list[Post | None] | Page:
    """Return the posts in the context.

    If there's a `post` in the context, then we return a list with that post.

    If there's a `posts` in the context, then we return the posts. The `posts` should
    be a Page object.

    Args:
        context: The context.

    Returns:
        list[Post]: The posts in the context.
    """
    post: Post | None = context.get("post")
    posts: Page | None = context.get("posts")

    if post:
        return [post]
    if posts:
        return posts

    return []


@register.simple_tag(takes_context=True)
def get_post_title(context: Context) -> str:
    """Return the title of a post.

    This is just the title of the post from the current context with no further HTML.

    Args:
        context: The context.

    Returns:
        str: The title of the post.
    """
    post: Post | None = context.get("post")
    if not post:
        return ""

    return post.title


@register.simple_tag(takes_context=True)
def post_title(context: Context, *, outer_tag: str = "", link_class: str = "", force_link: bool = False) -> str:
    """Return the title link for a post.

    If the post is part of a posts collection, then return the title and a link to the post. If the post is a single
    post, then return just the title of the post with no link. But this behavior can be overridden by setting
    `force_link` to `True`.

    The outer tag can be any of the following: "h1", "h2", "h3", "h4", "h5", "h6", "p", "div", "span". If the outer tag
    is not one of these, then the title will be returned with no outer tag.

    If the outer tag is one of the allowed tags, and if Microformats are enabled, then the outer tag will have the class
    "p-name".

    Otherwise return an empty string.

    Args:
        context: The context.
        outer_tag: The outer HTML tag for the title.
        link_class: The CSS class(es) for the link.
        force_link: Whether to force the link to be displayed.

    Returns:
        str: The title link for the post.
    """
    post: Post | None = context.get("post")
    posts: Page | None = context.get("posts")

    # If there's no post in the context, return an empty string.
    if not post:
        return ""

    # Get the title of the post
    output = post.title

    # If there's a posts in the context, or if the link is forced, then we need to display the link.
    if posts or force_link:
        link_class_html = f' class="{link_class}"' if link_class else ""

        output = f'<a href="{post.url}" title="{output}"{link_class_html}>{output}</a>'

    # If the outer tag is one of the allowed tags, then wrap the output in the outer tag.
    if outer_tag in ["h1", "h2", "h3", "h4", "h5", "h6", "p", "div", "span"]:
        # If Microformats are enabled, use p-name with the outer tag.
        mf = ' class="p-name"' if djpress_settings.MICROFORMATS_ENABLED else ""

        output = f"<{outer_tag}{mf}>{output}</{outer_tag}>"

    return mark_safe(output)


@register.simple_tag(takes_context=True)
def post_author(context: Context) -> str:
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
def post_author_link(context: Context, link_class: str = "") -> str:
    """Return the author link for a post.

    Args:
        context: The context.
        link_class: The CSS class(es) for the link.

    Returns:
        str: The author link.
    """
    post: Post | None = context.get("post")
    if not post:
        return ""

    author = post.author
    author_display_name = get_author_display_name(author)

    if not djpress_settings.AUTHOR_ENABLED:
        return f'<span rel="author">{author_display_name}</span>'

    author_url = url_utils.get_author_url(user=author)

    link_class_html = f' class="{link_class}"' if link_class else ""

    output = (
        f'<a href="{author_url}" title="View all posts by '
        f'{author_display_name}"{link_class_html}>'
        f'<span rel="author">{author_display_name}</span></a>'
    )

    return mark_safe(output)


@register.simple_tag
def post_category_link(category: Category, link_class: str = "") -> str:
    """Return the category links for a post.

    TODO: do we need this?

    Args:
        category: The category of the post.
        link_class: The CSS class(es) for the link.
    """
    if not djpress_settings.CATEGORY_ENABLED:
        return category.title

    return mark_safe(helpers.category_link(category, link_class))


@register.simple_tag(takes_context=True)
def post_date(context: Context) -> str:
    """Return the date of a post.

    Args:
        context: The context.

    Returns:
        str: The date of the post.
    """
    post: Post | None = context.get("post")
    if not post:
        return ""

    output_date = post.date
    return output_date.strftime("%b %-d, %Y")


@register.simple_tag(takes_context=True)
def post_date_link(context: Context, link_class: str = "") -> str:
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
    output_date = post.date

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

    return mark_safe(output)


@register.simple_tag(takes_context=True)
def post_content(
    context: Context,
    read_more_link_class: str = "",
    read_more_text: str = "",
) -> str:
    """Return the content of a post.

    If the post is part of a posts collection, then we return the truncated content of
    the post with the read more link.

    If the post is a single post, then return the full content of the post.

    Otherwise return and empty string.

    Args:
        context: The context.
        read_more_link_class: The CSS class(es) for the read more link.
        read_more_text: The text for the read more link.

    Returns:
        str: The content of the post.
    """
    # Check if there's a post or posts in the context.
    post: Post | None = context.get("post")
    posts: Page | None = context.get("posts")

    content: str = ""

    if posts and post:
        content = mark_safe(post.truncated_content_markdown)
        if post.is_truncated:
            content += helpers.post_read_more_link(post, read_more_link_class, read_more_text)
        return mark_safe(content)

    if post:
        return mark_safe(post.content_markdown)

    return content


@register.simple_tag(takes_context=True)
def category_title(
    context: Context,
    outer: str = "",
    outer_class: str = "",
    pre_text: str = "",
    post_text: str = "",
) -> str:
    """Return the title of a category.

    Expects there to be an `category` in the context set to a Category object. If
    there's no category in the context or category is not a Category object, then return
    an empty string.


    Args:
        context: The context.
        outer: The outer HTML tag for the category.
        outer_class: The CSS class(es) for the outer tag.
        pre_text: The text to prepend to the category title.
        post_text: The text to append to the category title.

    Returns:
        str: The title of the category formatted with the outer tag and class if
        provided.
    """
    category: Category | None = context.get("category")

    if not category or not isinstance(category, Category):
        return ""

    allowed_outer_tags = ["h1", "h2", "h3", "h4", "h5", "h6", "p", "div", "span"]
    outer_class = f' class="{outer_class}"' if outer_class else ""

    output = category.title

    if pre_text:
        output = f"{pre_text}{output}"

    if post_text:
        output = f"{output}{post_text}"

    if outer in allowed_outer_tags:
        return mark_safe(f"<{outer}{outer_class}>{output}</{outer}>")

    return output


@register.simple_tag(takes_context=True)
def author_name(
    context: Context,
    outer: str = "",
    outer_class: str = "",
    pre_text: str = "",
    post_text: str = "",
) -> str:
    """Return the name of an author.

    Expects there to be an `author` in the context set to a user object. If there's no
    author in the context or author is not a User object, then return an empty string.

    Args:
        context: The context.
        outer: The outer HTML tag for the author.
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

    allowed_outer_tags = ["h1", "h2", "h3", "h4", "h5", "h6", "p", "div", "span"]
    outer_class = f' class="{outer_class}"' if outer_class else ""

    output = get_author_display_name(author)

    if pre_text:
        output = f"{pre_text}{output}"

    if post_text:
        output = f"{output}{post_text}"

    if outer in allowed_outer_tags:
        return mark_safe(f"<{outer}{outer_class}>{output}</{outer}>")

    return output


@register.simple_tag(takes_context=True)
def post_categories_link(
    context: Context,
    outer: str = "ul",
    outer_class: str = "",
    link_class: str = "",
) -> str:
    """Return the categories of a post.

    Each category is a link to the category page.

    Args:
        context: The context.
        outer: The outer HTML tag for the categories.
        outer_class: The CSS class(es) for the outer tag.
        link_class: The CSS class(es) for the link.

    Returns:
        str: The categories of the post.
    """
    post: Post | None = context.get("post")
    if not post:
        return ""

    categories = post.categories.all()
    if not categories:
        return ""

    return mark_safe(helpers.categories_html(categories, outer, outer_class, link_class))


@register.simple_tag(takes_context=True)
def is_paginated(context: Context) -> bool:
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

    if page.has_previous():
        previous_output = (
            f'<span class="previous">'
            f'<a href="?page=1">&laquo; first</a> '
            f'<a href="?page={page.previous_page_number()}">previous</a>'
            f"</span>"
        )
    else:
        previous_output = ""

    if page.has_next():
        next_output = (
            f'<span class="next">'
            f'<a href="?page={page.next_page_number()}">next</a> '
            f'<a href="?page={page.paginator.num_pages}">last &raquo;</a>'
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
    outer: str = "div",
    outer_class: str = "",
    link_class: str = "",
) -> str:
    """Return the link to a page.

    Args:
        page_slug: The slug of the page.
        outer: The outer HTML tag for the page link.
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

    if outer == "li":
        return mark_safe(f"<li{outer_class}>{output}</li>")

    if outer == "span":
        return mark_safe(f"<span{outer_class}>{output}</span>")

    if outer == "div":
        return mark_safe(f"<div{outer_class}>{output}</div>")

    return mark_safe(output)


@register.simple_tag
def rss_url() -> str:
    """Return the URL to the RSS feed.

    Returns:
        str: The URL to the RSS feed.
    """
    return url_utils.get_rss_url()
