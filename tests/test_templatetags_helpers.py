import pytest

from django.contrib.auth.models import User

from djpress.conf import settings
from djpress.models import Category, Post
from djpress.templatetags.helpers import (
    categories_html,
    category_link,
    post_read_more_link,
)


@pytest.fixture
def user():
    user = User.objects.create_user(
        username="testuser",
        password="testpass",
        first_name="Test",
        last_name="User",
    )
    return user


@pytest.fixture
def category1():
    category = Category.objects.create(
        name="General",
        slug="general",
    )
    return category


@pytest.fixture
def category2():
    category = Category.objects.create(
        name="News",
        slug="news",
    )
    return category


@pytest.fixture
def category3():
    category = Category.objects.create(
        name="Development",
        slug="dev",
    )
    return category


@pytest.fixture
def test_post(user, category1):
    post = Post.post_objects.create(
        title="Test Post",
        slug="test-post",
        content="This is a test post.",
        author=user,
        status="published",
        post_type="post",
    )
    post.categories.set([category1])
    return post


@pytest.mark.django_db
def test_categories_html(category1, category2, category3):
    assert settings.CATEGORY_PATH == "test-url-category"

    categories = Category.objects.all()
    assert list(categories) == [category1, category2, category3]

    # Test case 1
    outer = "ul"
    outer_class = "categories"
    link_class = "category"
    expected_output = (
        '<ul class="categories">'
        f'<li><a href="/{settings.CATEGORY_PATH}/{category1.slug}/" title="View all posts in the {category1.name} category" class="{link_class}">{category1.name}</a></li>'
        f'<li><a href="/{settings.CATEGORY_PATH}/{category2.slug}/" title="View all posts in the {category2.name} category" class="{link_class}">{category2.name}</a></li>'
        f'<li><a href="/{settings.CATEGORY_PATH}/{category3.slug}/" title="View all posts in the {category3.name} category" class="{link_class}">{category3.name}</a></li>'
        "</ul>"
    )
    assert (
        categories_html(
            categories, outer=outer, outer_class=outer_class, link_class=link_class
        )
        == expected_output
    )

    # Test case 2
    outer = "ul"
    outer_class = ""
    link_class = ""
    expected_output = (
        "<ul>"
        f'<li><a href="/{settings.CATEGORY_PATH}/{category1.slug}/" title="View all posts in the {category1.name} category">{category1.name}</a></li>'
        f'<li><a href="/{settings.CATEGORY_PATH}/{category2.slug}/" title="View all posts in the {category2.name} category">{category2.name}</a></li>'
        f'<li><a href="/{settings.CATEGORY_PATH}/{category3.slug}/" title="View all posts in the {category3.name} category">{category3.name}</a></li>'
        "</ul>"
    )
    assert (
        categories_html(
            categories, outer=outer, outer_class=outer_class, link_class=link_class
        )
        == expected_output
    )

    # Test case 3
    outer = "div"
    outer_class = "categories"
    link_class = "category"
    expected_output = (
        '<div class="categories">'
        f'<a href="/{settings.CATEGORY_PATH}/{category1.slug}/" title="View all posts in the {category1.name} category" class="{link_class}">{category1.name}</a>, '
        f'<a href="/{settings.CATEGORY_PATH}/{category2.slug}/" title="View all posts in the {category2.name} category" class="{link_class}">{category2.name}</a>, '
        f'<a href="/{settings.CATEGORY_PATH}/{category3.slug}/" title="View all posts in the {category3.name} category" class="{link_class}">{category3.name}</a>'
        "</div>"
    )
    assert (
        categories_html(
            categories, outer=outer, outer_class=outer_class, link_class=link_class
        )
        == expected_output
    )

    # Test case 4
    outer = "div"
    outer_class = ""
    link_class = ""
    expected_output = (
        "<div>"
        f'<a href="/{settings.CATEGORY_PATH}/{category1.slug}/" title="View all posts in the {category1.name} category">{category1.name}</a>, '
        f'<a href="/{settings.CATEGORY_PATH}/{category2.slug}/" title="View all posts in the {category2.name} category">{category2.name}</a>, '
        f'<a href="/{settings.CATEGORY_PATH}/{category3.slug}/" title="View all posts in the {category3.name} category">{category3.name}</a>'
        "</div>"
    )
    assert (
        categories_html(
            categories, outer=outer, outer_class=outer_class, link_class=link_class
        )
        == expected_output
    )

    # Test case 5
    outer = "span"
    outer_class = "categories"
    link_class = "category"
    expected_output = (
        '<span class="categories">'
        f'<a href="/{settings.CATEGORY_PATH}/{category1.slug}/" title="View all posts in the {category1.name} category" class="{link_class}">{category1.name}</a>, '
        f'<a href="/{settings.CATEGORY_PATH}/{category2.slug}/" title="View all posts in the {category2.name} category" class="{link_class}">{category2.name}</a>, '
        f'<a href="/{settings.CATEGORY_PATH}/{category3.slug}/" title="View all posts in the {category3.name} category" class="{link_class}">{category3.name}</a>'
        "</span>"
    )
    assert (
        categories_html(
            categories, outer=outer, outer_class=outer_class, link_class=link_class
        )
        == expected_output
    )

    # Test case 6
    outer = "span"
    outer_class = ""
    link_class = ""
    expected_output = (
        "<span>"
        f'<a href="/{settings.CATEGORY_PATH}/{category1.slug}/" title="View all posts in the {category1.name} category">{category1.name}</a>, '
        f'<a href="/{settings.CATEGORY_PATH}/{category2.slug}/" title="View all posts in the {category2.name} category">{category2.name}</a>, '
        f'<a href="/{settings.CATEGORY_PATH}/{category3.slug}/" title="View all posts in the {category3.name} category">{category3.name}</a>'
        "</span>"
    )
    assert (
        categories_html(
            categories, outer=outer, outer_class=outer_class, link_class=link_class
        )
        == expected_output
    )


@pytest.mark.django_db
def testcategory_link(category1):
    assert settings.CATEGORY_PATH == "test-url-category"

    # Test case 1 - no link class
    link_class = ""
    expected_output = f'<a href="/{settings.CATEGORY_PATH}/{category1.slug}/" title="View all posts in the {category1.name} category">{category1.name}</a>'
    assert category_link(category1, link_class) == expected_output

    # Test case 2 - with link class
    link_class = "category-class"
    expected_output = f'<a href="/{settings.CATEGORY_PATH}/{category1.slug}/" title="View all posts in the {category1.name} category" class="{link_class}">{category1.name}</a>'
    assert category_link(category1, link_class) == expected_output


@pytest.mark.django_db
def test_post_read_more_link(test_post):
    assert settings.POST_READ_MORE_TEXT == "Test read more..."
    assert settings.POST_PREFIX == "test-posts"

    # Test case 1 - use the app settings for the read more text
    link_class = ""
    read_more_text = ""
    expected_output = f'<p><a href="/{settings.POST_PREFIX}/{test_post.slug}/">{settings.POST_READ_MORE_TEXT}</a></p>'
    assert post_read_more_link(test_post, link_class, read_more_text) == expected_output

    # Test case 2 - use all options
    link_class = "read-more"
    read_more_text = "Continue reading"
    expected_output = f'<p><a href="/{settings.POST_PREFIX}/{test_post.slug}/" class="{link_class}">{read_more_text}</a></p>'
    assert post_read_more_link(test_post, link_class, read_more_text) == expected_output
