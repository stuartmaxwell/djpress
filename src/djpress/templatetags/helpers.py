"""Helper functions for the template tags."""

from django import template
from django.db import models
from django.utils.safestring import mark_safe

from djpress.conf import settings as djpress_settings
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
    category_url = category.url

    link_classes = ""

    # Add p-category if microformats are enabled
    if djpress_settings.MICROFORMATS_ENABLED:
        link_classes += "p-category "

    # Add the user-defined link class
    link_classes += link_class

    # Trim any trailing spaces
    link_classes = link_classes.strip()

    link_class_html = f' class="{link_classes}"' if link_classes else ""

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
    page_url = page.url

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
    read_more_text = read_more_text if read_more_text else djpress_settings.POST_READ_MORE_TEXT
    link_class_html = f' class="{link_class}"' if link_class else ""

    return f'<p><a href="{post.url}"{link_class_html}>{read_more_text}</a></p>'


def get_blog_pages_list(
    pages: list[dict[Post, list]],
    li_class: str = "",
    a_class: str = "",
    ul_child_class: str = "",
) -> str:
    """Return the HTML for the blog pages list.

    This expects to be passed the output of the get_page_tree method.

    Args:
        pages: The pages from the get_page_tree method.
        li_class: The CSS class(es) for the list item.
        a_class: The CSS class(es) for the link.
        ul_child_class: The CSS class(es) for the child ul

    Returns:
        str: The HTML for the blog pages list.
    """
    class_li = f' class="{li_class}"' if li_class else ""
    class_ul = f' class="{ul_child_class}"' if ul_child_class else ""

    output = ""

    for page_data in pages:
        page = page_data["page"]
        children = page_data["children"]

        output += f"<li{class_li}>{get_page_link(page, link_class=a_class)}"

        if children:
            output += f"<ul{class_ul}>"
            output += get_blog_pages_list(children, li_class=li_class, a_class=a_class, ul_child_class=ul_child_class)
            output += "</ul>"

        output += "</li>"

    return output


class BlogPostWrapper(template.Node):
    """Wraps the blog post content.

    This is a template tag that wraps the blog post content in a configurable HTML tag with a CSS class.

    Args:
        nodelist: The content to wrap.
        tag: The HTML tag to wrap the content in.
        css_class: The CSS class(es) for the tag.

    Returns:
        str: The wrapped content.
    """

    def __init__(self, nodelist: template.NodeList, tag: str = "", css_class: str = "") -> None:
        """Initialize the BlogPostWrapper."""
        self.nodelist = nodelist
        self.tag = "article" if tag == "" else tag
        self.css_class = css_class

    def render(self, context: template.Context) -> str:
        """Render the blog post content."""
        content = self.nodelist.render(context)

        # Just return the content if the tag isn't allowed
        if self.tag not in ["div", "span", "section", "article"]:
            return mark_safe(content)

        return mark_safe(f"<{self.tag}{self.css_class}>{content}</{self.tag}>")


def parse_post_wrapper_params(params: list) -> tuple[str, str]:
    """Parse the parameters for the template tag.

    Args:
        params: The parameters for the template tag.

    Returns:
        tuple: The tag and CSS class.
    """
    tag = ""
    css_class = ""

    for num, param in enumerate(params):
        # Support keyword arguments
        if "=" in param:
            name, value = param.split("=", 1)
            value = value.strip("\"'")
            if name == "tag":
                tag = value
            elif name == "class":
                css_class = value
            else:
                # Ignore any other keyword arguments
                pass
        else:
            # Support positional arguments too
            value = param.strip("\"'")
            if num == 0:
                tag = value
            if num == 1:
                css_class = value

    return tag, css_class
