"""Template tags for djpress."""

from django import template
from django.conf import settings
from django.db import models
from django.template import Context
from django.urls import reverse
from django.utils.safestring import mark_safe

from djpress.models import Category, Post
from djpress.utils import get_author_display_name

register = template.Library()


@register.simple_tag
def get_categories() -> models.QuerySet[Category] | None:
    """Return all categories.

    Returns:
        models.QuerySet[Category]: All categories.
    """
    return Category.objects.get_categories()


@register.simple_tag
def get_recent_published_posts() -> models.QuerySet[Category] | None:
    """Return recent published posts from the cache.

    Returns:
        models.QuerySet[Category]: Recent published posts.
    """
    return Post.post_objects.get_recent_published_posts()


@register.simple_tag
def get_single_published_post(slug: str) -> Post | None:
    """Return a single published post by slug.

    Args:
        slug: The slug of the post.

    Returns:
        Post: A single published post.
    """
    return Post.post_objects.get_published_post_by_slug(slug)


@register.simple_tag
def get_blog_title() -> str:
    """Return the blog title.

    Returns:
        str: The blog title.
    """
    return settings.BLOG_TITLE


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


def category_link(category: Category, link_class: str = "") -> str:
    """Return the category link for a post.

    This is not intded to be used as a template tag. It is used by the other
    template tags in this module to generate the category links.

    Args:
        category: The category of the post.
        link_class: The CSS class(es) for the link.
    """
    category_url = reverse("djpress:category_posts", args=[category.slug])

    link_class_html = f' class="{link_class}"' if link_class else ""

    return (
        f'<a href="{category_url}" title="View all posts in the {category.name} '
        f'category"{link_class_html}>{ category.name }</a>'
    )


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
def post_content(context: Context) -> str:
    """Return the content of a post.

    Args:
        context: The context.

    Returns:
        str: The content of the post.
    """
    post: Post | None = context.get("post")
    if not post:
        return ""

    return mark_safe(post.content_markdown)


@register.simple_tag(takes_context=True)
def category_name(context: Context) -> str:
    """Return the name of a category.

    Args:
        context: The context.

    Returns:
        str: The name of the category.
    """
    category: Category | None = context.get("category")
    if not category:
        return ""

    return category.name


@register.simple_tag(takes_context=True)
def post_categories(context: Context, outer: str = "ul", link_class: str = "") -> str:
    """Return the categories of a post.

    Args:
        context: The context.
        outer: The outer HTML tag for the categories.
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

    output = ""

    if outer == "ul":
        output += "<ul>"
        for category in categories:
            output += f"<li>{category_link(category, link_class)}</li>"
        output += "</ul>"

    if outer == "div":
        output += "<div>"
        for category in categories:
            output += f"{category_link(category, link_class)}, "
        output = output[:-2]  # Remove the trailing comma and space
        output += "</div>"

    if outer == "span":
        output += "<span>"
        for category in categories:
            output += f"{category_link(category, link_class)}, "
        output = output[:-2]  # Remove the trailing comma and space
        output += "</span>"

    return mark_safe(output)
