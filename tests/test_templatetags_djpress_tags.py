import pytest
from django.contrib.auth.models import User
from django.template import Context
from django.urls import reverse
from django.utils import timezone

from djpress.conf import settings
from djpress.models import Category, Post
from djpress.templatetags import djpress_tags
from djpress.templatetags.helpers import post_read_more_link
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
def test_post1(user, category1):
    post = Post.post_objects.create(
        title="Test Post1",
        slug="test-post1",
        content="This is a test post.",
        author=user,
        status="published",
        post_type="post",
    )
    post.categories.set([category1])
    return post


@pytest.fixture
def test_long_post1(user, category1):
    post = Post.post_objects.create(
        title="Test Long Post1",
        slug="test-long-post1",
        content=f"This is the truncated content.\n\n{settings.TRUNCATE_TAG}\n\nThis is the rest of the post.",
        author=user,
        status="published",
        post_type="post",
    )
    post.categories.set([category1])
    return post


@pytest.mark.django_db
def test_have_posts_single_post(test_post1):
    """Return a list of posts in the context."""
    context = Context({"post": test_post1})

    assert djpress_tags.have_posts(context) == [test_post1]


@pytest.mark.django_db
def test_have_posts_no_posts():
    """Return an empty list if there are no posts in the context."""
    context = Context({"foo": "bar"})

    assert djpress_tags.have_posts(context) == []


@pytest.mark.django_db
def test_have_posts_multiple_posts(test_post1, test_long_post1):
    """Return a list of posts in the context."""
    context = Context({"posts": [test_post1, test_long_post1]})

    assert djpress_tags.have_posts(context) == [test_post1, test_long_post1]


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

    assert list(djpress_categories) == list(categories)  # type: ignore


@pytest.mark.django_db
def test_post_title_single_post(test_post1):
    context = Context({"post": test_post1})
    assert djpress_tags.post_title(context) == test_post1.title


def test_post_title_no_post_context():
    context = Context({"foo": "bar"})
    assert djpress_tags.post_title(context) == ""
    assert type(djpress_tags.post_title(context)) == str


@pytest.mark.django_db
def test_post_title_posts(test_post1):
    """Test the post_title_link template tag.

    This uses the post.permalink property to generate the link."""
    # Context should have both a posts and a post to simulate the for post in posts loop
    context = Context({"posts": [test_post1], "post": test_post1})

    # Confirm settings in settings_testing.py
    assert settings.POST_PREFIX == "test-posts"

    # this generates a URL based on the slug only - this is prefixed with the POST_PREFIX setting
    post_url = reverse("djpress:post_detail", args=[test_post1.slug])

    # Confirm settings in settings_testing.py
    assert settings.POST_PREFIX == "test-posts"
    expected_output = f'<a href="/test-posts{post_url}" title="{test_post1.title}">{test_post1.title}</a>'
    assert djpress_tags.post_title_link(context) == expected_output


@pytest.mark.django_db
def test_post_title_link_no_context():
    context = Context()

    expected_output = ""
    assert djpress_tags.post_title_link(context) == expected_output


@pytest.mark.django_db
def test_post_title_link_with_prefix(test_post1):
    # Confirm settings in settings_testing.py
    assert settings.POST_PREFIX == "test-posts"

    # Context should have both a posts and a post to simulate the for post in posts loop
    context = Context({"posts": [test_post1], "post": test_post1})

    post_url = reverse("djpress:post_detail", args=[test_post1.slug])

    expected_output = f'<a href="/test-posts{post_url}" title="{test_post1.title}">{test_post1.title}</a>'
    assert djpress_tags.post_title_link(context) == expected_output


@pytest.mark.django_db
def test_post_author(test_post1):
    context = Context({"post": test_post1})

    author = test_post1.author
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
def test_post_author_link(test_post1):
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.AUTHOR_PATH_ENABLED is True
    assert settings.AUTHOR_PATH == "test-url-author"

    author = test_post1.author

    expected_output = (
        f'<a href="/{settings.AUTHOR_PATH}/testuser/" title="View all posts by '
        f'{ get_author_display_name(author) }"><span rel="author">'
        f"{ get_author_display_name(author) }</span></a>"
    )
    assert djpress_tags.post_author_link(context) == expected_output


@pytest.mark.django_db
def test_post_author_link_author_path_disabled(test_post1):
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.AUTHOR_PATH_ENABLED is True
    assert settings.AUTHOR_PATH == "test-url-author"

    settings.set("AUTHOR_PATH_ENABLED", False)

    author = test_post1.author

    expected_output = f'<span rel="author">{get_author_display_name(author)}</span>'
    assert djpress_tags.post_author_link(context) == expected_output

    # Set back to defaults
    settings.set("AUTHOR_PATH_ENABLED", True)


@pytest.mark.django_db
def test_post_author_link_with_author_path_with_one_link_class(test_post1):
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.AUTHOR_PATH_ENABLED is True
    assert settings.AUTHOR_PATH == "test-url-author"

    author = test_post1.author

    expected_output = (
        f'<a href="/{settings.AUTHOR_PATH}/testuser/" title="View all posts by '
        f'{ get_author_display_name(author) }" class="class1">'
        f'<span rel="author">{ get_author_display_name(author) }</span></a>'
    )
    assert djpress_tags.post_author_link(context, "class1") == expected_output


@pytest.mark.django_db
def test_post_author_link_with_author_path_with_two_link_class(test_post1):
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.AUTHOR_PATH_ENABLED is True
    assert settings.AUTHOR_PATH == "test-url-author"

    author = test_post1.author

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
def test_post_date_with_date_archives_disabled(test_post1):
    """djpress_tags.post_date is not impacted by the DATE_ARCHIVES_ENABLED setting."""
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.DATE_ARCHIVES_ENABLED is True

    settings.set("DATE_ARCHIVES_ENABLED", False)
    assert settings.DATE_ARCHIVES_ENABLED is False

    expected_output = test_post1.date.strftime("%b %-d, %Y")

    assert djpress_tags.post_date(context) == expected_output

    # Set back to defaults
    settings.set("DATE_ARCHIVES_ENABLED", True)


@pytest.mark.django_db
def test_post_date_with_date_archives_enabled(test_post1):
    """djpress_tags.post_date is not impacted by the DATE_ARCHIVES_ENABLED setting."""
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.DATE_ARCHIVES_ENABLED is True

    expected_output = test_post1.date.strftime("%b %-d, %Y")

    assert djpress_tags.post_date(context) == expected_output


def test_post_date_link_no_post():
    context = Context({"foo": "bar"})

    assert djpress_tags.post_date_link(context) == ""
    assert type(djpress_tags.post_date_link(context)) == str


@pytest.mark.django_db
def test_post_date_link_with_date_archives_disabled(test_post1):
    """Should return just the date."""
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.DATE_ARCHIVES_ENABLED is True

    settings.set("DATE_ARCHIVES_ENABLED", False)
    assert settings.DATE_ARCHIVES_ENABLED is False

    expected_output = test_post1.date.strftime("%b %-d, %Y")

    assert djpress_tags.post_date_link(context) == expected_output

    # Set back to defaults
    settings.set("DATE_ARCHIVES_ENABLED", True)


@pytest.mark.django_db
def test_post_date_link_with_date_archives_enabled(test_post1):
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.DATE_ARCHIVES_ENABLED is True

    post_date = test_post1.date
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
    test_post1,
):
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.DATE_ARCHIVES_ENABLED is True

    post_date = test_post1.date
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
    test_post1,
):
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.DATE_ARCHIVES_ENABLED is True

    post_date = test_post1.date
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
    """If there's no post in the context, return an empty string."""
    context = Context({"foo": "bar"})

    assert djpress_tags.post_content(context) == ""
    assert type(djpress_tags.post_content(context)) == str


@pytest.mark.django_db
def test_post_content_with_post(test_post1):
    """If there's a post in the context, return the post content."""
    context = Context({"post": test_post1})

    expected_output = f"{test_post1.content_markdown}"

    assert djpress_tags.post_content(context) == expected_output


@pytest.mark.django_db
def test_post_content_with_posts(test_long_post1):
    """If there's a posts in the context, return the truncated post content."""
    # Context should have both a posts and a post to simulate the for post in posts loop
    context = Context({"posts": [test_long_post1], "post": test_long_post1})

    expected_output = (
        f"{test_long_post1.truncated_content_markdown}"
        f"{post_read_more_link(test_long_post1)}"
    )

    assert djpress_tags.post_content(context) == expected_output


@pytest.mark.django_db
def test_author_name(user):
    """author_name only works if there's a author in the context."""
    context = Context({"author": user})

    # Test case 1 - no options
    expected_output = get_author_display_name(user)
    assert djpress_tags.author_name(context) == expected_output

    # Test case 2 - with options
    expected_output = f'<h1 class="title">View posts in the {get_author_display_name(user)} author</h1>'
    assert (
        djpress_tags.author_name(
            context,
            outer="h1",
            outer_class="title",
            pre_text="View posts in the ",
            post_text=" author",
        )
        == expected_output
    )


def test_author_name_no_author():
    """If there's no author in the context, return an empty string."""
    context = Context({"foo": "bar"})

    assert djpress_tags.author_name(context) == ""
    assert type(djpress_tags.author_name(context)) == str


@pytest.mark.django_db
def test_category_name(category1):
    """category_name only works if there's a category in the context."""
    context = Context({"category": category1})

    # Test case 1 - no options
    expected_output = category1.name
    assert djpress_tags.category_name(context) == expected_output

    # Test case 2 - with options
    expected_output = (
        f'<h1 class="title">View posts in the {category1.name} category</h1>'
    )
    assert (
        djpress_tags.category_name(
            context,
            outer="h1",
            outer_class="title",
            pre_text="View posts in the ",
            post_text=" category",
        )
        == expected_output
    )


def test_category_name_no_category():
    """If there's no category in the context, return an empty string."""
    context = Context({"foo": "bar"})

    assert djpress_tags.category_name(context) == ""
    assert type(djpress_tags.category_name(context)) == str


@pytest.mark.django_db
def test_post_categories(test_post1):
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.CATEGORY_PATH == "test-url-category"

    expected_output = f'<ul><li><a href="/{settings.CATEGORY_PATH}/general/" title="View all posts in the General category">General</a></li></ul>'

    assert djpress_tags.post_categories_link(context) == expected_output


def test_post_categories_none_post_context():
    context = Context({"post": None})

    expected_output = ""
    assert djpress_tags.post_categories_link(context) == expected_output


def test_post_categories_no_post_context():
    context = Context({"foo": None})

    expected_output = ""
    assert djpress_tags.post_categories_link(context) == expected_output


@pytest.mark.django_db
def test_post_categories_no_categories_context(test_post1):
    test_post1.categories.clear()
    context = Context({"post": test_post1})

    expected_output = ""
    assert djpress_tags.post_categories_link(context) == expected_output


@pytest.mark.django_db
def test_post_categories_ul(test_post1):
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.CATEGORY_PATH == "test-url-category"

    expected_output = f'<ul><li><a href="/{settings.CATEGORY_PATH}/general/" title="View all posts in the General category">General</a></li></ul>'

    assert djpress_tags.post_categories_link(context, "ul") == expected_output


@pytest.mark.django_db
def test_post_categories_ul_class1(test_post1):
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.CATEGORY_PATH == "test-url-category"

    expected_output = f'<ul><li><a href="/{settings.CATEGORY_PATH}/general/" title="View all posts in the General category" class="class1">General</a></li></ul>'

    assert (
        djpress_tags.post_categories_link(context, outer="ul", link_class="class1")
        == expected_output
    )


@pytest.mark.django_db
def test_post_categories_ul_class1_class2(test_post1):
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.CATEGORY_PATH == "test-url-category"

    expected_output = f'<ul><li><a href="/{settings.CATEGORY_PATH}/general/" title="View all posts in the General category" class="class1 class2">General</a></li></ul>'

    assert (
        djpress_tags.post_categories_link(
            context, outer="ul", link_class="class1 class2"
        )
        == expected_output
    )


@pytest.mark.django_db
def test_post_categories_div(test_post1):
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.CATEGORY_PATH == "test-url-category"

    expected_output = f'<div><a href="/{settings.CATEGORY_PATH}/general/" title="View all posts in the General category">General</a></div>'

    assert djpress_tags.post_categories_link(context, outer="div") == expected_output


@pytest.mark.django_db
def test_post_categories_div_class1(test_post1):
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.CATEGORY_PATH == "test-url-category"

    expected_output = f'<div><a href="/{settings.CATEGORY_PATH}/general/" title="View all posts in the General category" class="class1">General</a></div>'

    assert (
        djpress_tags.post_categories_link(context, outer="div", link_class="class1")
        == expected_output
    )


@pytest.mark.django_db
def test_post_categories_div_class1_class2(test_post1):
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.CATEGORY_PATH == "test-url-category"

    expected_output = f'<div><a href="/{settings.CATEGORY_PATH}/general/" title="View all posts in the General category" class="class1 class2">General</a></div>'

    assert (
        djpress_tags.post_categories_link(
            context, outer="div", link_class="class1 class2"
        )
        == expected_output
    )


@pytest.mark.django_db
def test_post_categories_span(test_post1):
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.CATEGORY_PATH == "test-url-category"

    expected_output = f'<span><a href="/{settings.CATEGORY_PATH}/general/" title="View all posts in the General category">General</a></span>'

    assert djpress_tags.post_categories_link(context, outer="span") == expected_output


@pytest.mark.django_db
def test_post_categories_span_class1(test_post1):
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.CATEGORY_PATH == "test-url-category"

    expected_output = f'<span><a href="/{settings.CATEGORY_PATH}/general/" title="View all posts in the General category" class="class1">General</a></span>'

    assert (
        djpress_tags.post_categories_link(context, outer="span", link_class="class1")
        == expected_output
    )


@pytest.mark.django_db
def test_post_categories_span_class1_class2(test_post1):
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.CATEGORY_PATH == "test-url-category"

    expected_output = f'<span><a href="/{settings.CATEGORY_PATH}/general/" title="View all posts in the General category" class="class1 class2">General</a></span>'

    assert (
        djpress_tags.post_categories_link(
            context, outer="span", link_class="class1 class2"
        )
        == expected_output
    )
