import pytest

from django.contrib.auth.models import User

from djpress.conf import settings
from djpress.models import Category, Post, Tag
from djpress.templatetags.helpers import (
    categories_html,
    category_link,
    post_read_more_link,
    parse_post_wrapper_params,
    tags_html,
)


@pytest.mark.django_db
def test_categories_html(category1, category2, category3):
    assert settings.CATEGORY_PREFIX == "test-url-category"

    categories = Category.objects.all()
    assert list(categories) == [category1, category2, category3]

    # Test case 1
    outer = "ul"
    outer_class = "categories"
    link_class = "category"
    expected_output = (
        '<ul class="categories">'
        f'<li><a href="/{settings.CATEGORY_PREFIX}/{category1.slug}/" title="View all posts in the {category1.title} category" class="p-category {link_class}">{category1.title}</a></li>'
        f'<li><a href="/{settings.CATEGORY_PREFIX}/{category2.slug}/" title="View all posts in the {category2.title} category" class="p-category {link_class}">{category2.title}</a></li>'
        f'<li><a href="/{settings.CATEGORY_PREFIX}/{category3.slug}/" title="View all posts in the {category3.title} category" class="p-category {link_class}">{category3.title}</a></li>'
        "</ul>"
    )
    assert (
        categories_html(categories, outer_tag=outer, outer_class=outer_class, link_class=link_class) == expected_output
    )

    # Test case 2
    outer = "ul"
    outer_class = ""
    link_class = ""
    expected_output = (
        "<ul>"
        f'<li><a href="/{settings.CATEGORY_PREFIX}/{category1.slug}/" title="View all posts in the {category1.title} category" class="p-category">{category1.title}</a></li>'
        f'<li><a href="/{settings.CATEGORY_PREFIX}/{category2.slug}/" title="View all posts in the {category2.title} category" class="p-category">{category2.title}</a></li>'
        f'<li><a href="/{settings.CATEGORY_PREFIX}/{category3.slug}/" title="View all posts in the {category3.title} category" class="p-category">{category3.title}</a></li>'
        "</ul>"
    )
    assert (
        categories_html(categories, outer_tag=outer, outer_class=outer_class, link_class=link_class) == expected_output
    )

    # Test case 3
    outer = "div"
    outer_class = "categories"
    link_class = "category"
    expected_output = (
        '<div class="categories">'
        f'<a href="/{settings.CATEGORY_PREFIX}/{category1.slug}/" title="View all posts in the {category1.title} category" class="p-category {link_class}">{category1.title}</a>, '
        f'<a href="/{settings.CATEGORY_PREFIX}/{category2.slug}/" title="View all posts in the {category2.title} category" class="p-category {link_class}">{category2.title}</a>, '
        f'<a href="/{settings.CATEGORY_PREFIX}/{category3.slug}/" title="View all posts in the {category3.title} category" class="p-category {link_class}">{category3.title}</a>'
        "</div>"
    )
    assert (
        categories_html(categories, outer_tag=outer, outer_class=outer_class, link_class=link_class) == expected_output
    )

    # Test case 4
    outer = "div"
    outer_class = ""
    link_class = ""
    expected_output = (
        "<div>"
        f'<a href="/{settings.CATEGORY_PREFIX}/{category1.slug}/" title="View all posts in the {category1.title} category" class="p-category">{category1.title}</a>, '
        f'<a href="/{settings.CATEGORY_PREFIX}/{category2.slug}/" title="View all posts in the {category2.title} category" class="p-category">{category2.title}</a>, '
        f'<a href="/{settings.CATEGORY_PREFIX}/{category3.slug}/" title="View all posts in the {category3.title} category" class="p-category">{category3.title}</a>'
        "</div>"
    )
    assert (
        categories_html(categories, outer_tag=outer, outer_class=outer_class, link_class=link_class) == expected_output
    )

    # Test case 5
    outer = "span"
    outer_class = "categories"
    link_class = "category"
    expected_output = (
        '<span class="categories">'
        f'<a href="/{settings.CATEGORY_PREFIX}/{category1.slug}/" title="View all posts in the {category1.title} category" class="p-category {link_class}">{category1.title}</a>, '
        f'<a href="/{settings.CATEGORY_PREFIX}/{category2.slug}/" title="View all posts in the {category2.title} category" class="p-category {link_class}">{category2.title}</a>, '
        f'<a href="/{settings.CATEGORY_PREFIX}/{category3.slug}/" title="View all posts in the {category3.title} category" class="p-category {link_class}">{category3.title}</a>'
        "</span>"
    )
    assert (
        categories_html(categories, outer_tag=outer, outer_class=outer_class, link_class=link_class) == expected_output
    )

    # Test case 6
    outer = "span"
    outer_class = ""
    link_class = ""
    expected_output = (
        "<span>"
        f'<a href="/{settings.CATEGORY_PREFIX}/{category1.slug}/" title="View all posts in the {category1.title} category" class="p-category">{category1.title}</a>, '
        f'<a href="/{settings.CATEGORY_PREFIX}/{category2.slug}/" title="View all posts in the {category2.title} category" class="p-category">{category2.title}</a>, '
        f'<a href="/{settings.CATEGORY_PREFIX}/{category3.slug}/" title="View all posts in the {category3.title} category" class="p-category">{category3.title}</a>'
        "</span>"
    )
    assert (
        categories_html(categories, outer_tag=outer, outer_class=outer_class, link_class=link_class) == expected_output
    )


@pytest.mark.django_db
def test_tags_html(settings, tag1, tag2, tag3):
    assert settings.DJPRESS_SETTINGS["TAG_PREFIX"] == "test-url-tag"

    tags = Tag.objects.get_tags()
    assert list(tags) == [tag1, tag2, tag3]

    # Test case 1
    outer = "ul"
    outer_class = "tags"
    link_class = "tag"
    expected_output = (
        '<ul class="tags">'
        f'<li><a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag1.slug}/" title="View all posts tagged with {tag1.title}" class="p-category {link_class}">{tag1.title}</a></li>'
        f'<li><a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag2.slug}/" title="View all posts tagged with {tag2.title}" class="p-category {link_class}">{tag2.title}</a></li>'
        f'<li><a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag3.slug}/" title="View all posts tagged with {tag3.title}" class="p-category {link_class}">{tag3.title}</a></li>'
        "</ul>"
    )
    assert tags_html(tags, outer_tag=outer, outer_class=outer_class, link_class=link_class) == expected_output

    # Test case 2
    outer = "ul"
    outer_class = ""
    link_class = ""
    expected_output = (
        "<ul>"
        f'<li><a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag1.slug}/" title="View all posts tagged with {tag1.title}" class="p-category">{tag1.title}</a></li>'
        f'<li><a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag2.slug}/" title="View all posts tagged with {tag2.title}" class="p-category">{tag2.title}</a></li>'
        f'<li><a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag3.slug}/" title="View all posts tagged with {tag3.title}" class="p-category">{tag3.title}</a></li>'
        "</ul>"
    )
    assert tags_html(tags, outer_tag=outer, outer_class=outer_class, link_class=link_class) == expected_output

    # Test case 3
    outer = "div"
    outer_class = "tags"
    link_class = "tag"
    expected_output = (
        '<div class="tags">'
        f'<a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag1.slug}/" title="View all posts tagged with {tag1.title}" class="p-category {link_class}">{tag1.title}</a>, '
        f'<a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag2.slug}/" title="View all posts tagged with {tag2.title}" class="p-category {link_class}">{tag2.title}</a>, '
        f'<a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag3.slug}/" title="View all posts tagged with {tag3.title}" class="p-category {link_class}">{tag3.title}</a>'
        "</div>"
    )
    assert tags_html(tags, outer_tag=outer, outer_class=outer_class, link_class=link_class) == expected_output

    # Test case 4
    outer = "div"
    outer_class = ""
    link_class = ""
    expected_output = (
        "<div>"
        f'<a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag1.slug}/" title="View all posts tagged with {tag1.title}" class="p-category">{tag1.title}</a>, '
        f'<a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag2.slug}/" title="View all posts tagged with {tag2.title}" class="p-category">{tag2.title}</a>, '
        f'<a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag3.slug}/" title="View all posts tagged with {tag3.title}" class="p-category">{tag3.title}</a>'
        "</div>"
    )
    assert tags_html(tags, outer_tag=outer, outer_class=outer_class, link_class=link_class) == expected_output

    # Test case 5
    outer = "span"
    outer_class = "tags"
    link_class = "tag"
    expected_output = (
        '<span class="tags">'
        f'<a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag1.slug}/" title="View all posts tagged with {tag1.title}" class="p-category {link_class}">{tag1.title}</a>, '
        f'<a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag2.slug}/" title="View all posts tagged with {tag2.title}" class="p-category {link_class}">{tag2.title}</a>, '
        f'<a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag3.slug}/" title="View all posts tagged with {tag3.title}" class="p-category {link_class}">{tag3.title}</a>'
        "</span>"
    )
    assert tags_html(tags, outer_tag=outer, outer_class=outer_class, link_class=link_class) == expected_output

    # Test case 6
    outer = "span"
    outer_class = ""
    link_class = ""
    expected_output = (
        "<span>"
        f'<a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag1.slug}/" title="View all posts tagged with {tag1.title}" class="p-category">{tag1.title}</a>, '
        f'<a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag2.slug}/" title="View all posts tagged with {tag2.title}" class="p-category">{tag2.title}</a>, '
        f'<a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag3.slug}/" title="View all posts tagged with {tag3.title}" class="p-category">{tag3.title}</a>'
        "</span>"
    )
    assert tags_html(tags, outer_tag=outer, outer_class=outer_class, link_class=link_class) == expected_output

    # Test case 7
    outer = "span"
    outer_class = ""
    link_class = ""
    settings.DJPRESS_SETTINGS["MICROFORMATS_ENABLED"] = False
    expected_output = (
        "<span>"
        f'<a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag1.slug}/" title="View all posts tagged with {tag1.title}">{tag1.title}</a>, '
        f'<a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag2.slug}/" title="View all posts tagged with {tag2.title}">{tag2.title}</a>, '
        f'<a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag3.slug}/" title="View all posts tagged with {tag3.title}">{tag3.title}</a>'
        "</span>"
    )
    assert tags_html(tags, outer_tag=outer, outer_class=outer_class, link_class=link_class) == expected_output

    # Test case 8
    outer = "span"
    outer_class = "tags"
    link_class = "tag"
    expected_output = (
        '<span class="tags">'
        f'<a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag1.slug}/" title="View all posts tagged with {tag1.title}" class="{link_class}">{tag1.title}</a>, '
        f'<a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag2.slug}/" title="View all posts tagged with {tag2.title}" class="{link_class}">{tag2.title}</a>, '
        f'<a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag3.slug}/" title="View all posts tagged with {tag3.title}" class="{link_class}">{tag3.title}</a>'
        "</span>"
    )
    assert tags_html(tags, outer_tag=outer, outer_class=outer_class, link_class=link_class) == expected_output


@pytest.mark.django_db
def testcategory_link(category1):
    assert settings.CATEGORY_PREFIX == "test-url-category"

    # Test case 1 - no link class
    link_class = ""
    expected_output = f'<a href="/{settings.CATEGORY_PREFIX}/{category1.slug}/" title="View all posts in the {category1.title} category" class="p-category">{category1.title}</a>'
    assert category_link(category1, link_class) == expected_output

    # Test case 2 - with link class
    link_class = "category-class"
    expected_output = f'<a href="/{settings.CATEGORY_PREFIX}/{category1.slug}/" title="View all posts in the {category1.title} category" class="p-category {link_class}">{category1.title}</a>'
    assert category_link(category1, link_class) == expected_output


@pytest.mark.django_db
def test_post_read_more_link(test_post1):
    assert settings.POST_READ_MORE_TEXT == "Test read more..."
    assert settings.POST_PREFIX == "test-posts"

    # Test case 1 - use the app settings for the read more text
    link_class = ""
    read_more_text = ""
    expected_output = f'<p><a href="{test_post1.url}">{settings.POST_READ_MORE_TEXT}</a></p>'
    assert post_read_more_link(test_post1, link_class, read_more_text) == expected_output

    # Test case 2 - use all options
    link_class = "read-more"
    read_more_text = "Continue reading"
    expected_output = f'<p><a href="{test_post1.url}" class="{link_class}">{read_more_text}</a></p>'
    assert post_read_more_link(test_post1, link_class, read_more_text) == expected_output


def test_parse_post_wrapper_params():
    # Test case 1
    params = ['tag="div"', 'class="blog-post"']
    expected_output = ("div", "blog-post")
    assert parse_post_wrapper_params(params) == expected_output

    # Test case 2
    params = ['class="blog-post"']
    expected_output = ("", "blog-post")
    assert parse_post_wrapper_params(params) == expected_output

    # Test case 3
    params = ['"div"', '"blog-post"']
    expected_output = ("div", "blog-post")
    assert parse_post_wrapper_params(params) == expected_output

    # Test case 4
    params = ['"blog-post"']
    expected_output = ("blog-post", "")
    assert parse_post_wrapper_params(params) == expected_output

    # Test case 5
    params = ['""', '"blog-post"']
    expected_output = ("", "blog-post")
    assert parse_post_wrapper_params(params) == expected_output

    # Test case 6
    params = ['tag="div"', 'class="blog-post"', 'extra="extra"']
    expected_output = ("div", "blog-post")
    assert parse_post_wrapper_params(params) == expected_output
