"""Helper functions for the template tags."""

from django.db import models
from django.urls import reverse

from djpress.models import Category


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
