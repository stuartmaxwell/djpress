import pytest
from django.contrib.auth.models import User
from django.template import Context
from django.urls import reverse
from django.utils import timezone

from djpress.conf import settings
from djpress.models import Category, Post
from djpress.templatetags import djpress_tags
from djpress.utils import get_author_display_name


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
def create_test_post(user, category1):
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


def test_blog_title():
    """Test the blog_title template tag.

    This can be changed on the fly.
    """
    assert settings.BLOG_TITLE == "My Test DJ Press Blog"
    assert djpress_tags.blog_title() == settings.BLOG_TITLE

    # Change the title
    settings.set("BLOG_TITLE", "My New Blog Title")
    assert settings.BLOG_TITLE == "My New Blog Title"
    assert djpress_tags.blog_title() == settings.BLOG_TITLE

    # Set the title back to the original
    settings.set("BLOG_TITLE", "My Test DJ Press Blog")
    assert settings.BLOG_TITLE == "My Test DJ Press Blog"
    assert djpress_tags.blog_title() == settings.BLOG_TITLE


@pytest.mark.django_db
def test_get_categories(category1, category2, category3):
    categories = Category.objects.all()
    djpress_categories = djpress_tags.get_categories()

    assert category1 in categories
    assert category2 in categories
    assert category3 in categories
    assert category1 in djpress_categories
    assert category2 in djpress_categories
    assert category3 in djpress_categories

    # The following is only here to avoid type errors
    if not categories or not djpress_categories:
        return None

    assert list(djpress_categories) == list(categories)


@pytest.mark.django_db
def test_post_title(create_test_post):
    context = Context({"post": create_test_post})
    assert djpress_tags.post_title(context) == create_test_post.title


def test_post_title_no_post():
    context = Context({"foo": "bar"})
    assert djpress_tags.post_title(context) == ""
    assert type(djpress_tags.post_title(context)) == str


@pytest.mark.django_db
def test_post_title_link(create_test_post):
    """Test the post_title_link template tag.

    This uses the post.permalink property to generate the link."""
    context = Context({"post": create_test_post})

    # Confirm settings in settings_testing.py
    assert settings.POST_PREFIX == "test-posts"

    # this generates a URL based on the slug only - this is prefixed with the POST_PREFIX setting
    post_url = reverse("djpress:post_detail", args=[create_test_post.slug])

    # Confirm settings in settings_testing.py
    assert settings.POST_PREFIX == "test-posts"
    expected_output = f'<a href="/test-posts{post_url}" title="{create_test_post.title}">{create_test_post.title}</a>'
    assert djpress_tags.post_title_link(context) == expected_output


@pytest.mark.django_db
def test_post_title_link_no_context():
    context = Context()

    expected_output = ""
    assert djpress_tags.post_title_link(context) == expected_output


@pytest.mark.django_db
def test_post_title_link_with_prefix(create_test_post):
    # Confirm settings in settings_testing.py
    assert settings.POST_PREFIX == "test-posts"

    context = Context({"post": create_test_post})
    post_url = reverse("djpress:post_detail", args=[create_test_post.slug])

    expected_output = f'<a href="/test-posts{post_url}" title="{create_test_post.title}">{create_test_post.title}</a>'
    assert djpress_tags.post_title_link(context) == expected_output


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
def test_post_author_link(create_test_post):
    context = Context({"post": create_test_post})

    # Confirm settings are set according to settings_testing.py
    assert settings.AUTHOR_PATH_ENABLED is True
    assert settings.AUTHOR_PATH == "test-url-author"

    author = create_test_post.author

    expected_output = (
        f'<a href="/{settings.AUTHOR_PATH}/testuser/" title="View all posts by '
        f'{ get_author_display_name(author) }"><span rel="author">'
        f"{ get_author_display_name(author) }</span></a>"
    )
    assert djpress_tags.post_author_link(context) == expected_output


@pytest.mark.django_db
def test_post_author_link_with_author_path_with_one_link_class(create_test_post):
    context = Context({"post": create_test_post})

    # Confirm settings are set according to settings_testing.py
    assert settings.AUTHOR_PATH_ENABLED is True
    assert settings.AUTHOR_PATH == "test-url-author"

    author = create_test_post.author

    expected_output = (
        f'<a href="/{settings.AUTHOR_PATH}/testuser/" title="View all posts by '
        f'{ get_author_display_name(author) }" class="class1">'
        f'<span rel="author">{ get_author_display_name(author) }</span></a>'
    )
    assert djpress_tags.post_author_link(context, "class1") == expected_output


@pytest.mark.django_db
def test_post_author_link_with_author_path_with_two_link_class(create_test_post):
    context = Context({"post": create_test_post})

    # Confirm settings are set according to settings_testing.py
    assert settings.AUTHOR_PATH_ENABLED is True
    assert settings.AUTHOR_PATH == "test-url-author"

    author = create_test_post.author

    expected_output = (
        f'<a href="/{settings.AUTHOR_PATH}/testuser/" title="View all posts by '
        f'{ get_author_display_name(author) }" class="class1 class2">'
        f'<span rel="author">{ get_author_display_name(author) }</span></a>'
    )
    assert djpress_tags.post_author_link(context, "class1 class2") == expected_output


@pytest.mark.django_db
def test_post_category_link_without_category_path(category1):
    """Test the post_category_link template tag without the category path enabled.

    If the CATEGORY_PATH_ENABLED setting is False, the template tag should just return
    the category name, with no link."""
    # Confirm settings are set according to settings_testing.py
    assert settings.CATEGORY_PATH_ENABLED is True

    settings.set("CATEGORY_PATH_ENABLED", False)
    assert settings.CATEGORY_PATH_ENABLED is False

    assert djpress_tags.post_category_link(category1) == category1.name

    # Set back to defaults
    settings.set("CATEGORY_PATH_ENABLED", True)


@pytest.mark.django_db
def test_post_category_link_without_category_pathwith_one_link(category1):
    """Test the post_category_link template tag without the category path enabled.

    If the CATEGORY_PATH_ENABLED setting is False, the template tag should just return
    the category name, with no link."""
    # Confirm settings are set according to settings_testing.py
    assert settings.CATEGORY_PATH_ENABLED is True

    settings.set("CATEGORY_PATH_ENABLED", False)
    assert settings.CATEGORY_PATH_ENABLED is False

    assert djpress_tags.post_category_link(category1, "class1") == category1.name

    # Set back to defaults
    settings.set("CATEGORY_PATH_ENABLED", True)


@pytest.mark.django_db
def test_post_category_link_with_category_path(category1):
    # Confirm settings are set according to settings_testing.py
    assert settings.CATEGORY_PATH_ENABLED is True
    assert settings.CATEGORY_PATH == "test-url-category"

    expected_output = f'<a href="/{settings.CATEGORY_PATH}/general/" title="View all posts in the General category">{category1.name}</a>'

    assert djpress_tags.post_category_link(category1) == expected_output


@pytest.mark.django_db
def test_post_category_link_with_category_path_with_one_link_class(category1):
    # Confirm settings are set according to settings_testing.py
    assert settings.CATEGORY_PATH_ENABLED is True
    assert settings.CATEGORY_PATH == "test-url-category"

    expected_output = f'<a href="/{settings.CATEGORY_PATH}/general/" title="View all posts in the General category" class="class1">{category1.name}</a>'

    assert djpress_tags.post_category_link(category1, "class1") == expected_output


@pytest.mark.django_db
def test_post_category_link_with_category_path_with_two_link_classes(category1):
    # Confirm settings are set according to settings_testing.py
    assert settings.CATEGORY_PATH_ENABLED is True
    assert settings.CATEGORY_PATH == "test-url-category"

    expected_output = f'<a href="/{settings.CATEGORY_PATH}/general/" title="View all posts in the General category" class="class1 class2">{category1.name}</a>'

    assert (
        djpress_tags.post_category_link(category1, "class1 class2") == expected_output
    )


def test_post_date_no_post():
    context = Context({"foo": "bar"})

    assert djpress_tags.post_date(context) == ""
    assert type(djpress_tags.post_date(context)) == str


@pytest.mark.django_db
def test_post_date_with_date_archives_disabled(create_test_post):
    """djpress_tags.post_date is not impacted by the DATE_ARCHIVES_ENABLED setting."""
    context = Context({"post": create_test_post})

    # Confirm settings are set according to settings_testing.py
    assert settings.DATE_ARCHIVES_ENABLED is True

    settings.set("DATE_ARCHIVES_ENABLED", False)
    assert settings.DATE_ARCHIVES_ENABLED is False

    expected_output = create_test_post.date.strftime("%b %-d, %Y")

    assert djpress_tags.post_date(context) == expected_output

    # Set back to defaults
    settings.set("DATE_ARCHIVES_ENABLED", True)


@pytest.mark.django_db
def test_post_date_with_date_archives_enabled(create_test_post):
    """djpress_tags.post_date is not impacted by the DATE_ARCHIVES_ENABLED setting."""
    context = Context({"post": create_test_post})

    # Confirm settings are set according to settings_testing.py
    assert settings.DATE_ARCHIVES_ENABLED is True

    expected_output = create_test_post.date.strftime("%b %-d, %Y")

    assert djpress_tags.post_date(context) == expected_output


def test_post_date_link_no_post():
    context = Context({"foo": "bar"})

    assert djpress_tags.post_date_link(context) == ""
    assert type(djpress_tags.post_date_link(context)) == str


@pytest.mark.django_db
def test_post_date_link_with_date_archives_disabled(create_test_post):
    """Should return just the date."""
    context = Context({"post": create_test_post})

    # Confirm settings are set according to settings_testing.py
    assert settings.DATE_ARCHIVES_ENABLED is True

    settings.set("DATE_ARCHIVES_ENABLED", False)
    assert settings.DATE_ARCHIVES_ENABLED is False

    expected_output = create_test_post.date.strftime("%b %-d, %Y")

    assert djpress_tags.post_date_link(context) == expected_output

    # Set back to defaults
    settings.set("DATE_ARCHIVES_ENABLED", True)


@pytest.mark.django_db
def test_post_date_link_with_date_archives_enabled(create_test_post):
    context = Context({"post": create_test_post})

    # Confirm settings are set according to settings_testing.py
    assert settings.DATE_ARCHIVES_ENABLED is True

    post_date = create_test_post.date
    post_year = post_date.strftime("%Y")
    post_month = post_date.strftime("%m")
    post_month_name = post_date.strftime("%b")
    post_day = post_date.strftime("%d")
    post_day_name = post_date.strftime("%-d")
    post_time = post_date.strftime("%-I:%M %p")

    expected_output = (
        f'<a href="/archives/{post_year}/{post_month}/" title="View all posts in {post_month_name} {post_year}">{post_month_name}</a> '
        f'<a href="/archives/{post_year}/{post_month}/{post_day}/" title="View all posts on {post_day_name} {post_month_name} {post_year}">{post_day_name}</a>, '
        f'<a href="/archives/{post_year}/" title="View all posts in {post_year}">{post_year}</a>, '
        f"{post_time}."
    )

    assert djpress_tags.post_date_link(context) == expected_output


@pytest.mark.django_db
def test_post_date_link_with_date_archives_enabled_with_one_link_class(
    create_test_post,
):
    context = Context({"post": create_test_post})

    # Confirm settings are set according to settings_testing.py
    assert settings.DATE_ARCHIVES_ENABLED is True

    post_date = create_test_post.date
    post_year = post_date.strftime("%Y")
    post_month = post_date.strftime("%m")
    post_month_name = post_date.strftime("%b")
    post_day = post_date.strftime("%d")
    post_day_name = post_date.strftime("%-d")
    post_time = post_date.strftime("%-I:%M %p")

    expected_output = (
        f'<a href="/archives/{post_year}/{post_month}/" title="View all posts in {post_month_name} {post_year}" class="class1">{post_month_name}</a> '
        f'<a href="/archives/{post_year}/{post_month}/{post_day}/" title="View all posts on {post_day_name} {post_month_name} {post_year}" class="class1">{post_day_name}</a>, '
        f'<a href="/archives/{post_year}/" title="View all posts in {post_year}" class="class1">{post_year}</a>, '
        f"{post_time}."
    )

    assert djpress_tags.post_date_link(context, "class1") == expected_output


@pytest.mark.django_db
def test_post_date_link_with_date_archives_enabled_with_two_link_classes(
    create_test_post,
):
    context = Context({"post": create_test_post})

    # Confirm settings are set according to settings_testing.py
    assert settings.DATE_ARCHIVES_ENABLED is True

    post_date = create_test_post.date
    post_year = post_date.strftime("%Y")
    post_month = post_date.strftime("%m")
    post_month_name = post_date.strftime("%b")
    post_day = post_date.strftime("%d")
    post_day_name = post_date.strftime("%-d")
    post_time = post_date.strftime("%-I:%M %p")

    expected_output = (
        f'<a href="/archives/{post_year}/{post_month}/" title="View all posts in {post_month_name} {post_year}" class="class1 class2">{post_month_name}</a> '
        f'<a href="/archives/{post_year}/{post_month}/{post_day}/" title="View all posts on {post_day_name} {post_month_name} {post_year}" class="class1 class2">{post_day_name}</a>, '
        f'<a href="/archives/{post_year}/" title="View all posts in {post_year}" class="class1 class2">{post_year}</a>, '
        f"{post_time}."
    )

    assert djpress_tags.post_date_link(context, "class1 class2") == expected_output


def test_post_content_no_post():
    context = Context({"foo": "bar"})

    assert djpress_tags.post_content(context) == ""
    assert type(djpress_tags.post_content(context)) == str


@pytest.mark.django_db
def test_post_content(create_test_post):
    context = Context({"post": create_test_post})

    expected_output = f"<p>{create_test_post.content}</p>"

    assert djpress_tags.post_content(context) == expected_output


@pytest.mark.django_db
def test_category_name(category1):
    context = Context({"category": category1})

    assert djpress_tags.category_name(context) == category1.name


def test_category_name_no_category():
    context = Context({"foo": "bar"})

    assert djpress_tags.category_name(context) == ""
    assert type(djpress_tags.category_name(context)) == str


@pytest.mark.django_db
def test_post_categories(create_test_post):
    context = Context({"post": create_test_post})

    # Confirm settings are set according to settings_testing.py
    assert settings.CATEGORY_PATH == "test-url-category"

    expected_output = f'<ul><li><a href="/{settings.CATEGORY_PATH}/general/" title="View all posts in the General category">General</a></li></ul>'

    assert djpress_tags.post_categories(context) == expected_output


def test_post_categories_none_post_context():
    context = Context({"post": None})

    expected_output = ""
    assert djpress_tags.post_categories(context) == expected_output


def test_post_categories_no_post_context():
    context = Context({"foo": None})

    expected_output = ""
    assert djpress_tags.post_categories(context) == expected_output


@pytest.mark.django_db
def test_post_categories_no_categories_context(create_test_post):
    create_test_post.categories.clear()
    context = Context({"post": create_test_post})

    expected_output = ""
    assert djpress_tags.post_categories(context) == expected_output


@pytest.mark.django_db
def test_post_categories_ul(create_test_post):
    context = Context({"post": create_test_post})

    # Confirm settings are set according to settings_testing.py
    assert settings.CATEGORY_PATH == "test-url-category"

    expected_output = f'<ul><li><a href="/{settings.CATEGORY_PATH}/general/" title="View all posts in the General category">General</a></li></ul>'

    assert djpress_tags.post_categories(context, "ul") == expected_output


@pytest.mark.django_db
def test_post_categories_ul_class1(create_test_post):
    context = Context({"post": create_test_post})

    # Confirm settings are set according to settings_testing.py
    assert settings.CATEGORY_PATH == "test-url-category"

    expected_output = f'<ul><li><a href="/{settings.CATEGORY_PATH}/general/" title="View all posts in the General category" class="class1">General</a></li></ul>'

    assert (
        djpress_tags.post_categories(context, outer="ul", link_class="class1")
        == expected_output
    )


@pytest.mark.django_db
def test_post_categories_ul_class1_class2(create_test_post):
    context = Context({"post": create_test_post})

    # Confirm settings are set according to settings_testing.py
    assert settings.CATEGORY_PATH == "test-url-category"

    expected_output = f'<ul><li><a href="/{settings.CATEGORY_PATH}/general/" title="View all posts in the General category" class="class1 class2">General</a></li></ul>'

    assert (
        djpress_tags.post_categories(context, outer="ul", link_class="class1 class2")
        == expected_output
    )


@pytest.mark.django_db
def test_post_categories_div(create_test_post):
    context = Context({"post": create_test_post})

    # Confirm settings are set according to settings_testing.py
    assert settings.CATEGORY_PATH == "test-url-category"

    expected_output = f'<div><a href="/{settings.CATEGORY_PATH}/general/" title="View all posts in the General category">General</a></div>'

    assert djpress_tags.post_categories(context, outer="div") == expected_output


@pytest.mark.django_db
def test_post_categories_div_class1(create_test_post):
    context = Context({"post": create_test_post})

    # Confirm settings are set according to settings_testing.py
    assert settings.CATEGORY_PATH == "test-url-category"

    expected_output = f'<div><a href="/{settings.CATEGORY_PATH}/general/" title="View all posts in the General category" class="class1">General</a></div>'

    assert (
        djpress_tags.post_categories(context, outer="div", link_class="class1")
        == expected_output
    )


@pytest.mark.django_db
def test_post_categories_div_class1_class2(create_test_post):
    context = Context({"post": create_test_post})

    # Confirm settings are set according to settings_testing.py
    assert settings.CATEGORY_PATH == "test-url-category"

    expected_output = f'<div><a href="/{settings.CATEGORY_PATH}/general/" title="View all posts in the General category" class="class1 class2">General</a></div>'

    assert (
        djpress_tags.post_categories(context, outer="div", link_class="class1 class2")
        == expected_output
    )


@pytest.mark.django_db
def test_post_categories_span(create_test_post):
    context = Context({"post": create_test_post})

    # Confirm settings are set according to settings_testing.py
    assert settings.CATEGORY_PATH == "test-url-category"

    expected_output = f'<span><a href="/{settings.CATEGORY_PATH}/general/" title="View all posts in the General category">General</a></span>'

    assert djpress_tags.post_categories(context, outer="span") == expected_output


@pytest.mark.django_db
def test_post_categories_span_class1(create_test_post):
    context = Context({"post": create_test_post})

    # Confirm settings are set according to settings_testing.py
    assert settings.CATEGORY_PATH == "test-url-category"

    expected_output = f'<span><a href="/{settings.CATEGORY_PATH}/general/" title="View all posts in the General category" class="class1">General</a></span>'

    assert (
        djpress_tags.post_categories(context, outer="span", link_class="class1")
        == expected_output
    )


@pytest.mark.django_db
def test_post_categories_span_class1_class2(create_test_post):
    context = Context({"post": create_test_post})

    # Confirm settings are set according to settings_testing.py
    assert settings.CATEGORY_PATH == "test-url-category"

    expected_output = f'<span><a href="/{settings.CATEGORY_PATH}/general/" title="View all posts in the General category" class="class1 class2">General</a></span>'

    assert (
        djpress_tags.post_categories(context, outer="span", link_class="class1 class2")
        == expected_output
    )
