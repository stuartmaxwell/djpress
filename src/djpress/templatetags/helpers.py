"""Helper functions for the template tags."""

from django.db import models
from django.urls import reverse

from djpress.conf import settings
from djpress.models import Category, Post


def categories_html(
    categories: models.QuerySet,
    outer: str,
    outer_class: str,
    link_class: str,
) -> str:
    """Return the HTML for the categories.

    Note this isn't a template tag, but a helper function for the other template tags

    Args:
        categories: The categories.
        outer: The outer HTML tag for the categories.
        outer_class: The CSS class(es) for the outer tag.
        link_class: The CSS class(es) for the link.

    Returns:
        str: The HTML for the categories.
    """
    output = ""

    outer_class_html = f' class="{outer_class}"' if outer_class else ""

    if outer == "ul":
        output += f"<ul{outer_class_html}>"
        for category in categories:
            output += f"<li>{category_link(category, link_class)}</li>"
        output += "</ul>"

    if outer == "div":
        output += f"<div{outer_class_html}>"
        for category in categories:
            output += f"{category_link(category, link_class)}, "
        output = output[:-2]  # Remove the trailing comma and space
        output += "</div>"

    if outer == "span":
        output += f"<span{outer_class_html}>"
        for category in categories:
            output += f"{category_link(category, link_class)}, "
        output = output[:-2]  # Remove the trailing comma and space
        output += "</span>"

    return output


def category_link(category: Category, link_class: str = "") -> str:
    """Return the category link.

    This is not intended to be used as a template tag. It is used by the other
    template tags in this module to generate the category links.

    Args:
        category: The category.
        link_class: The CSS class(es) for the link.
    """
    category_url = reverse("djpress:category_posts", kwargs={"slug": category.slug})

    link_class_html = f' class="{link_class}"' if link_class else ""

    return (
        f'<a href="{category_url}" title="View all posts in the {category.title} '
        f'category"{link_class_html}>{category.title}</a>'
    )


def get_page_link(page: Post, link_class: str = "") -> str:
    """Return the page link.

    This is not intended to be used as a template tag. It is used by the other
    template tags in this module to generate the page links.

    Args:
        page: The page.
        link_class: The CSS class(es) for the link.
    """
    page_url = reverse("djpress:single_page", kwargs={"path": page.slug})

    link_class_html = f' class="{link_class}"' if link_class else ""

    return f'<a href="{page_url}" title="View the {page.title} page"{link_class_html}>{page.title}</a>'


def post_read_more_link(
    post: Post,
    link_class: str = "",
    read_more_text: str = "",
) -> str:
    """Return the read more link for a post.

    Args:
        post: The post.
        link_class: The CSS class(es) for the link.
        read_more_text: The text for the read more link.

    Returns:
        str: The read more link.
    """
    read_more_text = read_more_text if read_more_text else settings.POST_READ_MORE_TEXT
    link_class_html = f' class="{link_class}"' if link_class else ""

    return f'<p><a href="{post.url}"{link_class_html}>{read_more_text}</a></p>'
