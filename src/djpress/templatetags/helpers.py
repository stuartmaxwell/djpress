"""Helper functions for the template tags."""

from django import template
from django.db import models
from django.utils.safestring import mark_safe

from djpress.conf import settings as djpress_settings
from djpress.models import Category, Post, Tag
from djpress.models.post import PageNode


def categories_html(
    categories: models.QuerySet,
    outer_tag: str,
    outer_class: str,
    link_class: str,
    separator: str,
    pre_text: str,
    post_text: str,
) -> str:
    """Return the HTML for the categories.

    Note this isn't a template tag, but a helper function for the other template tags

    Args:
        categories: The categories.
        outer_tag: The outer HTML tag for the categories.
        outer_class: The CSS class(es) for the outer tag.
        link_class: The CSS class(es) for the link.
        separator: The separator between categories.
        pre_text: The text to display before the categories.
        post_text: The text to display after the categories.

    Returns:
        str: The HTML for the categories.
    """
    output = ""

    outer_class_html = f' class="{outer_class}"' if outer_class else ""

    if outer_tag == "ul":
        output += f"<ul{outer_class_html}>"
        for category in categories:
            output += f"<li>{category_link(category, link_class)}</li>"
        output += "</ul>"

    if outer_tag == "div":
        output += f"<div{outer_class_html}>{pre_text}"
        for category in categories:
            output += f"{category_link(category, link_class)}{separator}"
        output = output[: -len(separator)]  # Remove the trailing separator
        output += f"{post_text}</div>"

    if outer_tag == "span":
        output += f"<span{outer_class_html}>{pre_text}"
        for category in categories:
            output += f"{category_link(category, link_class)}{separator}"
        output = output[: -len(separator)]  # Remove the trailing separator
        output += f"{post_text}</span>"

    return output


def tags_html(
    tags: models.QuerySet,
    outer_tag: str,
    outer_class: str,
    link_class: str,
    separator: str,
    pre_text: str,
    post_text: str,
) -> str:
    """Return the HTML for the tags.

    Note this isn't a template tag, but a helper function for the other template tags

    Args:
        tags: The tags.
        outer_tag: The outer HTML tag for the tags.
        outer_class: The CSS class(es) for the outer tag.
        link_class: The CSS class(es) for the link.
        separator: The separator between tags.
        pre_text: The text to display before the tags.
        post_text: The text to display after the tags.

    Returns:
        str: The HTML for the tags.
    """
    output = ""

    outer_class_html = f' class="{outer_class}"' if outer_class else ""

    if outer_tag == "ul":
        output += f"<ul{outer_class_html}>"
        for tag in tags:
            output += f"<li>{tag_link(tag, link_class)}</li>"
        output += "</ul>"
    else:
        output += f"<{outer_tag}{outer_class_html}>{pre_text}"
        for tag in tags:
            output += f"{tag_link(tag, link_class)}{separator}"
        output = output[: -len(separator)]  # Remove the trailing separator
        output += f"{post_text}</{outer_tag}>"

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


def tag_link(tag: "Tag", link_class: str = "") -> str:
    """Return the tag link.

    This is not intended to be used as a template tag. It is used by the other
    template tags in this module to generate the tag links.

    Args:
        tag: The tag.
        link_class: The CSS class(es) for the link.
    """
    tag_url = tag.url

    link_classes = ""

    # Add p-category if microformats are enabled
    if djpress_settings.MICROFORMATS_ENABLED:
        link_classes += "p-category "

    # Add the user-defined link class
    link_classes += link_class

    # Trim any trailing spaces
    link_classes = link_classes.strip()

    link_class_html = f' class="{link_classes}"' if link_classes else ""

    return f'<a href="{tag_url}" title="View all posts tagged with {tag.title}"{link_class_html}>{tag.title}</a>'


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

    If the post isn't truncated, return an empty string.

    Args:
        post: The post.
        link_class: The CSS class(es) for the link.
        read_more_text: The text for the read more link.

    Returns:
        str: The read more link.
    """
    post_read_more_text = djpress_settings.POST_READ_MORE_TEXT

    # The following line should never be true since we assign a default value.
    if not isinstance(post_read_more_text, str):  # pragma: no cover
        msg = f"Expected a string for POST_READ_MORE_TEXT, got {type(post_read_more_text).__name__}"
        raise TypeError(msg)

    if post.is_truncated is False:
        return ""

    read_more_text = read_more_text if read_more_text else post_read_more_text
    link_class_html = f' class="{link_class}"' if link_class else ""

    return f'<p><a href="{post.url}"{link_class_html}>{read_more_text}</a></p>'


def get_site_pages_list(
    pages: list[PageNode],
    li_class: str = "",
    a_class: str = "",
    ul_child_class: str = "",
    levels: int = 0,
) -> str:
    """Return the HTML for the site pages list.

    This expects to be passed the output of the get_page_tree method.

    Args:
        pages: The pages from the get_page_tree method.
        li_class: The CSS class(es) for the list item.
        a_class: The CSS class(es) for the link.
        ul_child_class: The CSS class(es) for the child ul
        levels: The maximum depth of nested pages to include or 0 for unlimited.

    Returns:
        str: The HTML for the site pages list.
    """
    class_li = f' class="{li_class}"' if li_class else ""
    class_ul = f' class="{ul_child_class}"' if ul_child_class else ""

    output = ""

    for page_data in pages:
        page = page_data["page"]
        children = page_data["children"]

        output += f"<li{class_li}>{get_page_link(page, link_class=a_class)}"

        if children and (levels == 0 or levels > 1):
            new_levels = levels - 1 if levels > 0 else 0
            output += f"<ul{class_ul}>"
            output += get_site_pages_list(
                children,
                li_class=li_class,
                a_class=a_class,
                ul_child_class=ul_child_class,
                levels=new_levels,
            )
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
