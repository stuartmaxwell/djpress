"""Template tags for djpress."""

from django import template
from django.contrib.auth.models import User
from django.core.paginator import Page
from django.db import models
from django.template import Context
from django.urls import reverse
from django.utils.safestring import mark_safe

from djpress.conf import settings
from djpress.models import Category, Post
from djpress.templatetags.helpers import (
    categories_html,
    category_link,
    post_read_more_link,
)
from djpress.utils import get_author_display_name

register = template.Library()


@register.simple_tag
def blog_title() -> str:
    """Return the blog title.

    Returns:
        str: The blog title.
    """
    return settings.BLOG_TITLE


@register.simple_tag
def blog_title_link(link_class: str = "") -> str:
    """Return the blog title.

    Args:
        link_class: The CSS class(es) for the link.

    Returns:
        str: The blog title.
    """
    link_class_html = f' class="{link_class}"' if link_class else ""

    ouptut = (
        f'<a href="{reverse("djpress:index")}"{link_class_html}>'
        f'{settings.BLOG_TITLE}</a>'
    )

    return mark_safe(ouptut)


@register.simple_tag
def get_categories() -> models.QuerySet[Category] | None:
    """Return all categories as a queryset.

    Returns:
        models.QuerySet[Category]: All categories.
    """
    return Category.objects.get_categories()


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

    return mark_safe(categories_html(categories, outer, outer_class, link_class))


@register.simple_tag(takes_context=True)
def have_posts(context: Context) -> list[Post | None] | Page:
    """Return the posts in the context.

    If there's a `_post` in the context, then we return a list with that post.

    If there's a `_posts` in the context, then we return the posts. The `_posts` should
    be a Page object.

    Args:
        context: The context.

    Returns:
        list[Post]: The posts in the context.
    """
    post: Post | None = context.get("_post")
    posts: Page | None = context.get("_posts")

    if post:
        return [post]
    if posts:
        return posts

    return []


@register.simple_tag(takes_context=True)
def post_title(context: Context) -> str:
    """Return the title of a post.

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
def post_title_link(context: Context, link_class: str = "") -> str:
    """Return the title link for a post.

    Args:
        context: The context.
        link_class: The CSS class(es) for the link.

    Returns:
        str: The title link for the post.
    """
    post: Post | None = context.get("post")
    if not post:
        return ""

    _post: Post | None = context.get("_post")
    if _post:
        return post_title(context)

    post_url = reverse("djpress:post_detail", args=[post.permalink])

    link_class_html = f' class="{link_class}"' if link_class else ""

    output = (
        f'<a href="{post_url}" title="{post.title}"{link_class_html}>'
        f"{post.title}</a>"
    )

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
    author_display_name = get_author_display_name(author)

    return mark_safe(f'<span rel="author">{author_display_name}</span>')


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

    if not settings.AUTHOR_PATH_ENABLED:
        return f'<span rel="author">{author_display_name}</span>'

    author_url = reverse("djpress:author_posts", args=[author])

    link_class_html = f' class="{link_class}"' if link_class else ""

    output = (
        f'<a href="{author_url}" title="View all posts by '
        f'{ author_display_name }"{link_class_html}>'
        f'<span rel="author">{ author_display_name }</span></a>'
    )

    return mark_safe(output)


@register.simple_tag
def post_category_link(category: Category, link_class: str = "") -> str:
    """Return the category links for a post.

    Args:
        category: The category of the post.
        link_class: The CSS class(es) for the link.
    """
    if not settings.CATEGORY_PATH_ENABLED:
        return category.name

    return mark_safe(category_link(category, link_class))


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

    post_date = post.date
    return mark_safe(post_date.strftime("%b %-d, %Y"))


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
    post_date = post.date

    if not settings.DATE_ARCHIVES_ENABLED:
        return mark_safe(post_date.strftime("%b %-d, %Y"))

    post_year = post_date.strftime("%Y")
    post_month = post_date.strftime("%m")
    post_month_name = post_date.strftime("%b")
    post_day = post_date.strftime("%d")
    post_day_name = post_date.strftime("%-d")
    post_time = post_date.strftime("%-I:%M %p")

    year_url = reverse(
        "djpress:archives_posts",
        args=[post_year],
    )
    month_url = reverse(
        "djpress:archives_posts",
        args=[post_year, post_month],
    )
    day_url = reverse(
        "djpress:archives_posts",
        args=[
            post_year,
            post_month,
            post_day,
        ],
    )

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

    If there's no post in the context, then we return an empty string. If there are
    multiple posts in the context, then we return the truncated content of the post with
    the read more link. Otherwise, we return the full content of the post.

    Args:
        context: The context.
        read_more_link_class: The CSS class(es) for the read more link.
        read_more_text: The text for the read more link.

    Returns:
        str: The content of the post.
    """
    content: str = ""

    # Check if there's a post or _posts in the context.
    post: Post | None = context.get("post")
    _posts: models.QuerySet[Post] | None = context.get("_posts")

    # If there's no post, then we return an empty string.
    if not post:
        return content

    # If there are _posts, then we return the truncated content of the post.
    if _posts:
        content = mark_safe(post.truncated_content_markdown)
        if post.is_truncated:
            content += post_read_more_link(post, read_more_link_class, read_more_text)
        return mark_safe(content)

    # If there
    return mark_safe(post.content_markdown)


@register.simple_tag(takes_context=True)
def category_name(
    context: Context,
    outer: str = "",
    outer_class: str = "",
    pre_text: str = "",
    post_text: str = "",
) -> str:
    """Return the name of a category.

    Expects there to be an `category` in the context set to a Category object. If
    there's no category in the context or category is not a Category object, then retun
    an empty string.


    Args:
        context: The context.
        outer: The outer HTML tag for the category.
        outer_class: The CSS class(es) for the outer tag.
        pre_text: The text to prepend to the category name.
        post_text: The text to append to the category name.

    Returns:
        str: The name of the category formatted with the outer tag and class if
        provided.
    """
    category: Category | None = context.get("category")

    if not category or not isinstance(category, Category):
        return ""

    allowed_outer_tags = ["h1", "h2", "h3", "h4", "h5", "h6", "p", "div", "span"]
    outer_class = f' class="{outer_class}"' if outer_class else ""

    output = category.name

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
    """Return the name of a author.

    Expects there to be an `author` in the context set to a user object. If there's no
    author in the context or author is not a User object, then retun an empty string.

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

    return mark_safe(categories_html(categories, outer, outer_class, link_class))


@register.simple_tag(takes_context=True)
def posts_nav_links(
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

    current_output = (
        f'<span class="current">'
        f"Page {page.number} of {page.paginator.num_pages}"
        f"</span>"
    )

    return mark_safe(
        f'<div class="pagination">'
        f"{previous_output} {current_output} {next_output}"
        "</div>",
    )
