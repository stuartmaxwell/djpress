import pytest

from django.urls import reverse
from django.contrib.auth.models import User
from djpress.models import Post, Category
from django.conf import settings
from django.utils import timezone
from djpress.utils import get_author_display_name
from django.template import Context

from djpress.templatetags import djpress_tags


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
def category():
    category = Category.objects.create(
        name="Test Category",
        slug="test-category",
    )
    return category


@pytest.fixture
def create_test_post(user, category):
    post = Post.post_objects.create(
        title="Test Post",
        slug="test-post",
        content="This is a test post.",
        author=user,
        status="published",
        post_type="post",
    )
    post.categories.set([category])
    return post


def test_get_blog_title():
    assert djpress_tags.get_blog_title() == settings.BLOG_TITLE


@pytest.mark.django_db
def test_post_title(create_test_post):
    context = Context({"post": create_test_post})
    assert djpress_tags.post_title(context) == create_test_post.title


def test_post_title_no_post():
    context = Context({"foo": "bar"})
    assert djpress_tags.post_title(context) == ""
    assert type(djpress_tags.post_title(context)) == str


@pytest.mark.django_db
def test_post_author(create_test_post):
    context = Context({"post": create_test_post})

    author = create_test_post.author
    output = f'<span rel="author">{ get_author_display_name(author) }</span>'
    assert djpress_tags.post_author(context) == output


def test_post_author_no_post():
    context = Context({"foo": "bar"})
    assert djpress_tags.post_author(context) == ""
    assert type(djpress_tags.post_author(context)) == str


def test_post_author_link_no_post():
    context = Context({"foo": "bar"})
    assert djpress_tags.post_author_link(context) == ""
    assert type(djpress_tags.post_author_link(context)) == str


@pytest.mark.django_db
def test_post_author_link_without_author_path(create_test_post):
    context = Context({"post": create_test_post})
    settings.AUTHOR_PATH_ENABLED = False

    author = create_test_post.author
    output = f'<span rel="author">{ get_author_display_name(author) }</span>'
    assert djpress_tags.post_author_link(context) == output


@pytest.mark.django_db
def test_post_author_link_with_author_path(create_test_post):
    context = Context({"post": create_test_post})
    settings.AUTHOR_PATH_ENABLED = True

    author = create_test_post.author
    author_url = reverse("djpress:author_posts", args=[author])

    expected_output = (
        f'<a href="{author_url}" title="View all posts by '
        f'{ get_author_display_name(author) }"><span rel="author">'
        f"{ get_author_display_name(author) }</span></a>"
    )
    assert djpress_tags.post_author_link(context) == expected_output


@pytest.mark.django_db
def test_post_author_link_with_author_path_with_one_link_class(create_test_post):
    context = Context({"post": create_test_post})
    settings.AUTHOR_PATH_ENABLED = True

    author = create_test_post.author
    author_url = reverse("djpress:author_posts", args=[author])

    expected_output = (
        f'<a href="{author_url}" title="View all posts by '
        f'{ get_author_display_name(author) }" class="class1">'
        f'<span rel="author">{ get_author_display_name(author) }</span></a>'
    )
    assert djpress_tags.post_author_link(context, "class1") == expected_output


@pytest.mark.django_db
def test_post_author_link_with_author_path_with_two_link_class(create_test_post):
    context = Context({"post": create_test_post})
    settings.AUTHOR_PATH_ENABLED = True

    author = create_test_post.author
    author_url = reverse("djpress:author_posts", args=[author])

    expected_output = (
        f'<a href="{author_url}" title="View all posts by '
        f'{ get_author_display_name(author) }" class="class1 class2">'
        f'<span rel="author">{ get_author_display_name(author) }</span></a>'
    )
    assert djpress_tags.post_author_link(context, "class1 class2") == expected_output


@pytest.mark.django_db
def test_post_category_link_without_category_path(category):
    settings.CATEGORY_PATH_ENABLED = False
    assert djpress_tags.post_category_link(category) == category.name


@pytest.mark.django_db
def test_post_category_link_with_category_path(category):
    settings.CATEGORY_PATH_ENABLED = True
    category_url = reverse("djpress:category_posts", args=[category.slug])
    expected_output = f'<a href="{category_url}" title="View all posts in the Test Category category">{category.name}</a>'
    assert djpress_tags.post_category_link(category) == expected_output


@pytest.mark.django_db
def test_post_category_link_with_category_path_with_one_link_class(category):
    settings.CATEGORY_PATH_ENABLED = True
    category_url = reverse("djpress:category_posts", args=[category.slug])
    expected_output = f'<a href="{category_url}" title="View all posts in the Test Category category" class="class1">{category.name}</a>'
    assert djpress_tags.post_category_link(category, "class1") == expected_output


@pytest.mark.django_db
def test_post_category_link_with_category_path_with_two_link_classes(category):
    settings.CATEGORY_PATH_ENABLED = True
    category_url = reverse("djpress:category_posts", args=[category.slug])
    expected_output = f'<a href="{category_url}" title="View all posts in the Test Category category" class="class1 class2">{category.name}</a>'
    assert djpress_tags.post_category_link(category, "class1 class2") == expected_output


def test_post_date_no_post():
    context = Context({"foo": "bar"})
    assert djpress_tags.post_date(context) == ""
    assert type(djpress_tags.post_date(context)) == str


@pytest.mark.django_db
def test_post_date_without_date_archives_enabled(create_test_post):
    context = Context({"post": create_test_post})
    settings.DATE_ARCHIVES_ENABLED = False

    output = create_test_post.date.strftime("%b %-d, %Y")
    assert djpress_tags.post_date(context) == output


@pytest.mark.django_db
def test_post_date_with_date_archives_enabled(create_test_post):
    context = Context({"post": create_test_post})
    settings.DATE_ARCHIVES_ENABLED = True

    output = create_test_post.date.strftime("%b %-d, %Y")
    assert djpress_tags.post_date(context) == output


def test_post_date_link_no_post():
    context = Context({"foo": "bar"})
    assert djpress_tags.post_date_link(context) == ""
    assert type(djpress_tags.post_date_link(context)) == str


@pytest.mark.django_db
def test_post_date_link_without_date_archives_enabled(create_test_post):
    context = Context({"post": create_test_post})
    settings.DATE_ARCHIVES_ENABLED = False

    output = create_test_post.date.strftime("%b %-d, %Y")
    assert djpress_tags.post_date_link(context) == output


@pytest.mark.django_db
def test_post_date_link_with_date_archives_enabled(create_test_post):
    context = Context({"post": create_test_post})
    settings.DATE_ARCHIVES_ENABLED = True

    post_date = create_test_post.date
    post_year = post_date.strftime("%Y")
    post_month = post_date.strftime("%m")
    post_month_name = post_date.strftime("%b")
    post_day = post_date.strftime("%d")
    post_day_name = post_date.strftime("%-d")
    post_time = post_date.strftime("%-I:%M %p")

    output = (
        f'<a href="/archives/{post_year}/{post_month}/" title="View all posts in {post_month_name} {post_year}">{post_month_name}</a> '
        f'<a href="/archives/{post_year}/{post_month}/{post_day}/" title="View all posts on {post_day_name} {post_month_name} {post_year}">{post_day_name}</a>, '
        f'<a href="/archives/{post_year}/" title="View all posts in {post_year}">{post_year}</a>, '
        f"{post_time}."
    )

    assert djpress_tags.post_date_link(context) == output


@pytest.mark.django_db
def test_post_date_link_with_date_archives_enabled_with_one_link_class(
    create_test_post,
):
    context = Context({"post": create_test_post})
    settings.DATE_ARCHIVES_ENABLED = True

    post_date = create_test_post.date
    post_year = post_date.strftime("%Y")
    post_month = post_date.strftime("%m")
    post_month_name = post_date.strftime("%b")
    post_day = post_date.strftime("%d")
    post_day_name = post_date.strftime("%-d")
    post_time = post_date.strftime("%-I:%M %p")

    output = (
        f'<a href="/archives/{post_year}/{post_month}/" title="View all posts in {post_month_name} {post_year}" class="class1">{post_month_name}</a> '
        f'<a href="/archives/{post_year}/{post_month}/{post_day}/" title="View all posts on {post_day_name} {post_month_name} {post_year}" class="class1">{post_day_name}</a>, '
        f'<a href="/archives/{post_year}/" title="View all posts in {post_year}" class="class1">{post_year}</a>, '
        f"{post_time}."
    )

    assert djpress_tags.post_date_link(context, "class1") == output


@pytest.mark.django_db
def test_post_date_link_with_date_archives_enabled_with_two_link_classes(
    create_test_post,
):
    context = Context({"post": create_test_post})
    settings.DATE_ARCHIVES_ENABLED = True

    post_date = create_test_post.date
    post_year = post_date.strftime("%Y")
    post_month = post_date.strftime("%m")
    post_month_name = post_date.strftime("%b")
    post_day = post_date.strftime("%d")
    post_day_name = post_date.strftime("%-d")
    post_time = post_date.strftime("%-I:%M %p")

    output = (
        f'<a href="/archives/{post_year}/{post_month}/" title="View all posts in {post_month_name} {post_year}" class="class1 class2">{post_month_name}</a> '
        f'<a href="/archives/{post_year}/{post_month}/{post_day}/" title="View all posts on {post_day_name} {post_month_name} {post_year}" class="class1 class2">{post_day_name}</a>, '
        f'<a href="/archives/{post_year}/" title="View all posts in {post_year}" class="class1 class2">{post_year}</a>, '
        f"{post_time}."
    )

    assert djpress_tags.post_date_link(context, "class1 class2") == output


def test_post_content_no_post():
    context = Context({"foo": "bar"})
    assert djpress_tags.post_content(context) == ""
    assert type(djpress_tags.post_content(context)) == str


@pytest.mark.django_db
def test_post_content(create_test_post):
    context = Context({"post": create_test_post})

    output = f"<p>{create_test_post.content}</p>"
    assert djpress_tags.post_content(context) == output


@pytest.mark.django_db
def test_category_name(category):
    context = Context({"category": category})
    assert djpress_tags.category_name(context) == category.name


def test_category_name_no_category():
    context = Context({"foo": "bar"})
    assert djpress_tags.category_name(context) == ""
    assert type(djpress_tags.category_name(context)) == str


@pytest.mark.django_db
def test_post_categories(create_test_post):
    context = Context({"post": create_test_post})

    categories = create_test_post.categories.all()
    output = '<ul><li><a href="/category/test-category/" title="View all posts in the Test Category category">Test Category</a></li></ul>'
    assert djpress_tags.post_categories(context) == output


@pytest.mark.django_db
def test_post_categories_ul(create_test_post):
    context = Context({"post": create_test_post})

    output = '<ul><li><a href="/category/test-category/" title="View all posts in the Test Category category">Test Category</a></li></ul>'
    assert djpress_tags.post_categories(context, "ul") == output


@pytest.mark.django_db
def test_post_categories_ul_class1(create_test_post):
    context = Context({"post": create_test_post})

    output = '<ul><li><a href="/category/test-category/" title="View all posts in the Test Category category" class="class1">Test Category</a></li></ul>'
    assert (
        djpress_tags.post_categories(context, outer="ul", link_class="class1") == output
    )


@pytest.mark.django_db
def test_post_categories_ul_class1_class2(create_test_post):
    context = Context({"post": create_test_post})

    output = '<ul><li><a href="/category/test-category/" title="View all posts in the Test Category category" class="class1 class2">Test Category</a></li></ul>'
    assert (
        djpress_tags.post_categories(context, outer="ul", link_class="class1 class2")
        == output
    )


@pytest.mark.django_db
def test_post_categories_div(create_test_post):
    context = Context({"post": create_test_post})

    output = '<div><a href="/category/test-category/" title="View all posts in the Test Category category">Test Category</a></div>'
    assert djpress_tags.post_categories(context, outer="div") == output


@pytest.mark.django_db
def test_post_categories_div_class1(create_test_post):
    context = Context({"post": create_test_post})

    output = '<div><a href="/category/test-category/" title="View all posts in the Test Category category" class="class1">Test Category</a></div>'
    assert (
        djpress_tags.post_categories(context, outer="div", link_class="class1")
        == output
    )


@pytest.mark.django_db
def test_post_categories_div_class1_class2(create_test_post):
    context = Context({"post": create_test_post})

    output = '<div><a href="/category/test-category/" title="View all posts in the Test Category category" class="class1 class2">Test Category</a></div>'
    assert (
        djpress_tags.post_categories(context, outer="div", link_class="class1 class2")
        == output
    )


@pytest.mark.django_db
def test_post_categories_span(create_test_post):
    context = Context({"post": create_test_post})

    output = '<span><a href="/category/test-category/" title="View all posts in the Test Category category">Test Category</a></span>'
    assert djpress_tags.post_categories(context, outer="span") == output


@pytest.mark.django_db
def test_post_categories_span_class1(create_test_post):
    context = Context({"post": create_test_post})

    output = '<span><a href="/category/test-category/" title="View all posts in the Test Category category" class="class1">Test Category</a></span>'
    assert (
        djpress_tags.post_categories(context, outer="span", link_class="class1")
        == output
    )


@pytest.mark.django_db
def test_post_categories_span_class1_class2(create_test_post):
    context = Context({"post": create_test_post})

    output = '<span><a href="/category/test-category/" title="View all posts in the Test Category category" class="class1 class2">Test Category</a></span>'
    assert (
        djpress_tags.post_categories(context, outer="span", link_class="class1 class2")
        == output
    )
