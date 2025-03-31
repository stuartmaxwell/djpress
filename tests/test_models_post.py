import pytest
from django.utils import timezone
from unittest.mock import Mock
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db.models import QuerySet

from djpress.models import Category, Post
from djpress import urls as djpress_urls
from djpress.models.post import PUBLISHED_POSTS_CACHE_KEY
from djpress.exceptions import PostNotFoundError, PageNotFoundError


@pytest.mark.django_db
def test_post_model(test_post1, user, category1):
    test_post1.categories.add(category1)
    assert test_post1.title == "Test Post1"
    assert test_post1.slug == "test-post1"
    assert test_post1.author == user
    assert test_post1.status == "published"
    assert test_post1.post_type == "post"
    assert test_post1.categories.count() == 1
    assert str(test_post1) == "Test Post1"


@pytest.mark.django_db
def test_post_default_queryset(test_post1, test_post2, test_post3):
    """Make sure the default queryset returns only published posts."""
    assert list(Post.objects.all()) == [test_post1, test_post2, test_post3]

    test_post1.status = "draft"
    test_post1.save()
    assert list(Post.objects.all()) == [test_post2, test_post3]

    test_post2.date = timezone.now() + timezone.timedelta(days=1)
    test_post2.save()
    assert list(Post.objects.all()) == [test_post3]


@pytest.mark.django_db
def test_get_published_content_with_future_date(user):
    Post.post_objects.create(
        title="Past Post",
        slug="past-post",
        content="This is a past post.",
        author=user,
        status="published",
        post_type="post",
        date=timezone.now() - timezone.timedelta(days=1),
    )
    Post.post_objects.create(
        title="Future Post",
        slug="future-post",
        content="This is a future post.",
        author=user,
        status="published",
        post_type="post",
        date=timezone.now() + timezone.timedelta(days=1),
    )
    assert Post.admin_objects.all().count() == 2
    assert Post.post_objects.get_published_posts().count() == 1


@pytest.mark.django_db
def test_get_published_content_ordering(user):
    Post.post_objects.create(
        title="Older Post",
        slug="older-post",
        content="This is an older post.",
        author=user,
        status="published",
        post_type="post",
        date=timezone.now() - timezone.timedelta(days=2),
    )
    Post.post_objects.create(
        title="Newer Post",
        slug="newer-post",
        content="This is a newer post.",
        author=user,
        status="published",
        post_type="post",
        date=timezone.now() - timezone.timedelta(days=1),
    )
    posts = Post.post_objects.all()
    assert posts[0].title == "Newer Post"
    assert posts[1].title == "Older Post"


@pytest.mark.django_db
def test_get_published_post_by_slug_with_future_date(user):
    Post.post_objects.create(
        title="Future Post",
        slug="future-post",
        content="This is a future post.",
        author=user,
        status="published",
        post_type="post",
        date=timezone.now() + timezone.timedelta(days=1),
    )
    with pytest.raises(PostNotFoundError):
        Post.post_objects.get_published_post_by_slug("future-post")


@pytest.mark.django_db
def test_get_published_content_by_category_with_future_date(user):
    category = Category.objects.create(title="Test Category", slug="test-category")
    Post.post_objects.create(
        title="Past Post",
        slug="past-post",
        content="This is a past post.",
        author=user,
        status="published",
        post_type="post",
        date=timezone.now() - timezone.timedelta(days=1),
    ).categories.add(category)
    Post.post_objects.create(
        title="Future Post",
        slug="future-post",
        content="This is a future post.",
        author=user,
        status="published",
        post_type="post",
        date=timezone.now() + timezone.timedelta(days=1),
    ).categories.add(category)
    assert Post.post_objects.get_published_posts_by_category(category).count() == 1


@pytest.mark.django_db
def test_post_slug_generation(user):
    # Test case 1: Slug generated from title
    post1 = Post.post_objects.create(
        title="My First Blog Post",
        content="This is the content of my first blog post.",
        author=user,
    )
    assert post1.slug == "my-first-blog-post"

    # Test case 2: Slug not overridden when provided
    post2 = Post.post_objects.create(
        title="My Second Blog Post",
        slug="custom-slug",
        content="This is the content of my second blog post.",
        author=user,
    )
    assert post2.slug == "custom-slug"

    # Test case 3: Slug generated with special characters
    post3 = Post.post_objects.create(
        title="My Third Blog Post!",
        content="This is the content of my third blog post.",
        author=user,
    )
    assert post3.slug == "my-third-blog-post"

    # Test case 4: Slug generated with non-ASCII characters
    post4 = Post.post_objects.create(
        title="My Post with 😊 Emoji",
        content="This is the content of the post with an emoji in the title.",
        author=user,
    )
    assert post4.slug == "my-post-with-emoji"

    # Test case 5: Raise error for invalid title
    with pytest.raises(ValueError) as exc_info:
        Post.post_objects.create(
            title="!@#$%^&*()",
            content="This is the content of the post with an invalid title.",
            author=user,
        )
    assert str(exc_info.value) == "Invalid title. Unable to generate a valid slug."


@pytest.mark.django_db
def test_post_markdown_rendering(user, settings):
    with pytest.raises(KeyError):
        assert settings.DJPRESS_SETTINGS["MARKDOWN_EXTENSIONS"] == []

    # Test case 1: Render markdown with basic formatting
    post1 = Post.post_objects.create(
        title="Post with Markdown",
        content="# Heading\n\nThis is a paragraph with **bold** and *italic* text.",
        author=user,
    )
    expected_html = "<h1>Heading</h1>\n<p>This is a paragraph with <strong>bold</strong> and <em>italic</em> text.</p>"
    assert post1.content_markdown == expected_html


@pytest.mark.django_db
def test_post_truncated_content_markdown(user, settings):
    # Confirm the truncate tag is set according to settings_testing.py
    truncate_tag = "<!--test-more-->"
    assert settings.DJPRESS_SETTINGS["TRUNCATE_TAG"] == truncate_tag

    # Test case 1: Content with "read more" tag
    post1 = Post.post_objects.create(
        title="Post with Read More",
        content=f"This is the intro.\n\n{truncate_tag}\n\nThis is the rest of the content.",
        author=user,
    )
    expected_truncated_content = "<p>This is the intro.</p>"
    assert post1.truncated_content_markdown == expected_truncated_content

    # Test case 2: Content without "read more" tag
    post2 = Post.post_objects.create(
        title="Post without Read More",
        content="This is the entire content.",
        author=user,
    )
    expected_truncated_content = "<p>This is the entire content.</p>"
    assert post2.truncated_content_markdown == expected_truncated_content


@pytest.mark.django_db
def test_post_is_truncated_property(user, settings):
    # Confirm the truncate tag is set according to settings_testing.py
    truncate_tag = "<!--test-more-->"
    assert settings.DJPRESS_SETTINGS["TRUNCATE_TAG"] == truncate_tag

    # Test case 1: Content with truncate tag
    post1 = Post.post_objects.create(
        title="Post with Truncate Tag",
        content=f"This is the intro.{truncate_tag}This is the rest of the content.",
        author=user,
    )
    assert post1.is_truncated is True

    # Test case 2: Content without truncate tag
    post2 = Post.post_objects.create(
        title="Post without Truncate Tag",
        content="This is the entire content.",
        author=user,
    )
    assert post2.is_truncated is False

    # Test case 3: Content with truncate tag at the beginning
    post3 = Post.post_objects.create(
        title="Post with Truncate Tag at the Beginning",
        content=f"{truncate_tag}This is the content.",
        author=user,
    )
    assert post3.is_truncated is True

    # Test case 4: Content with truncate tag at the end
    post4 = Post.post_objects.create(
        title="Post with Truncate Tag at the End",
        content=f"This is the content.{truncate_tag}",
        author=user,
    )
    assert post4.is_truncated is True


@pytest.mark.django_db
def test_get_published_posts_by_author(user):
    # Create some published posts by the test user
    post1 = Post.post_objects.create(
        title="Post 1",
        content="Content of post 1.",
        author=user,
        status="published",
    )
    post2 = Post.post_objects.create(
        title="Post 2",
        content="Content of post 2.",
        author=user,
        status="published",
    )

    # Create a draft post by the test user
    draft_post = Post.post_objects.create(
        title="Draft Post",
        content="Content of draft post.",
        author=user,
        status="draft",
    )

    # Create a future post by the test user
    future_post = Post.post_objects.create(
        title="Future Post",
        content="Content of future post.",
        author=user,
        status="published",
        date=timezone.now() + timezone.timedelta(days=1),
    )

    # Call the method being tested
    published_posts = Post.post_objects.get_published_posts_by_author(user)

    # Assert that only the published posts by the test user are returned
    assert post1 in published_posts
    assert post2 in published_posts
    assert draft_post not in published_posts
    assert future_post not in published_posts


@pytest.mark.django_db
def test_get_recent_published_posts(user, settings):
    """Test that the get_recent_published_posts method returns the correct posts."""
    # Confirm settings are set according to settings_testing.py
    assert settings.DJPRESS_SETTINGS["CACHE_RECENT_PUBLISHED_POSTS"] is False
    assert settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] == 3

    # Create some published posts
    post1 = Post.objects.create(title="Post 1", status="published", author=user, content="Test post")
    post2 = Post.objects.create(title="Post 2", status="published", author=user, content="Test post")
    post3 = Post.objects.create(title="Post 3", status="published", author=user, content="Test post")

    # Call the method being tested
    recent_posts = Post.post_objects.get_recent_published_posts()

    # Assert that the correct posts are returned
    assert list(recent_posts) == [post3, post2, post1]

    # Test case 2: Limit the number of posts returned
    settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] = 2

    assert settings.DJPRESS_SETTINGS["CACHE_RECENT_PUBLISHED_POSTS"] is False
    assert settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] == 2

    # Call the method being tested again
    recent_posts = Post.post_objects.get_recent_published_posts()

    # Assert that the correct posts are returned
    assert list(recent_posts) == [post3, post2]
    assert post1 not in recent_posts


@pytest.mark.django_db
def test_get_published_page_by_slug(test_page1):
    """Test that the get_published_page_by_slug method returns the correct page."""
    assert test_page1 == Post.page_objects.get_published_page_by_slug("test-page1")

    with pytest.raises(PageNotFoundError):
        Post.page_objects.get_published_page_by_slug("non-existent-page")


@pytest.mark.django_db
def test_get_published_pages(test_page1, test_page2, test_page3, test_page4, test_page5):
    """Test that the get_published_pages method returns the correct pages."""
    assert list(Post.page_objects.get_published_pages()) == [test_page1, test_page2, test_page3, test_page4, test_page5]

    test_page1.status = "draft"
    test_page1.save()
    assert list(Post.page_objects.get_published_pages()) == [test_page2, test_page3, test_page4, test_page5]

    test_page2.parent = test_page1
    test_page2.save()
    assert list(Post.page_objects.get_published_pages()) == [test_page3, test_page4, test_page5]

    test_page3.date = timezone.now() + timezone.timedelta(days=1)
    test_page3.save()
    assert list(Post.page_objects.get_published_pages()) == [test_page4, test_page5]

    test_page4.parent = test_page3
    test_page4.save()
    test_page5.parent = test_page4
    test_page5.save()
    assert list(Post.page_objects.get_published_pages()) == []


@pytest.mark.django_db
def test_get_published_page_by_path_top_level(test_page1):
    """Test that the get_published_page_by_path method returns the correct page."""

    assert test_page1 == Post.page_objects.get_published_page_by_path(f"/test-page1")
    assert test_page1 == Post.page_objects.get_published_page_by_path(f"test-page1/")
    assert test_page1 == Post.page_objects.get_published_page_by_path(f"/test-page1/")
    assert test_page1 == Post.page_objects.get_published_page_by_path(f"//////test-page1/////")


@pytest.mark.django_db
def test_get_published_page_by_path_parent(test_page1, test_page2):
    """Test that the get_published_page_by_path method returns the correct page."""
    test_page1.parent = test_page2
    test_page1.save()

    assert test_page1 == Post.page_objects.get_published_page_by_path(f"/test-page2/test-page1")
    assert test_page1 == Post.page_objects.get_published_page_by_path(f"test-page2/test-page1/")
    assert test_page1 == Post.page_objects.get_published_page_by_path(f"/test-page2/test-page1/")
    assert test_page1 == Post.page_objects.get_published_page_by_path(f"//////test-page2/test-page1/////")


@pytest.mark.django_db
def test_get_published_page_by_path_grandparent(test_page1, test_page2, test_page3):
    """Test that the get_published_page_by_path method returns the correct page."""
    test_page1.parent = test_page2
    test_page1.save()
    test_page2.parent = test_page3
    test_page2.save()

    assert test_page1 == Post.page_objects.get_published_page_by_path(f"/test-page3/test-page2/test-page1")
    assert test_page1 == Post.page_objects.get_published_page_by_path(f"test-page3/test-page2/test-page1/")
    assert test_page1 == Post.page_objects.get_published_page_by_path(f"/test-page3/test-page2/test-page1/")
    assert test_page1 == Post.page_objects.get_published_page_by_path(f"//////test-page3/test-page2/test-page1/////")


@pytest.mark.django_db
def test_get_published_page_with_draft_parent(test_page1, test_page2, test_page3):
    """Test that the get_published_page_by_path method returns the correct page."""
    test_page1.parent = test_page2
    test_page1.save()

    assert test_page1 == Post.page_objects.get_published_page_by_path(f"/test-page2/test-page1")

    test_page2.status = "draft"
    test_page2.save()

    with pytest.raises(PageNotFoundError):
        Post.page_objects.get_published_page_by_path(f"/test-page2/test-page1")


@pytest.mark.django_db
def test_get_published_page_with_draft_grandparent(test_page1, test_page2, test_page3):
    """Test that the get_published_page_by_path method returns the correct page."""
    test_page1.parent = test_page2
    test_page1.save()
    test_page2.parent = test_page3
    test_page2.save()

    assert test_page1 == Post.page_objects.get_published_page_by_path(f"/test-page3/test-page2/test-page1")

    test_page3.status = "draft"
    test_page3.save()

    with pytest.raises(PageNotFoundError):
        Post.page_objects.get_published_page_by_path(f"/test-page3/test-page2/test-page1")


@pytest.mark.django_db
def test_get_non_existent_page_by_path():
    """Test that the get_published_page_by_path method raises a PageNotFoundError."""
    with pytest.raises(PageNotFoundError):
        Post.page_objects.get_published_page_by_path("non-existent-page")
    with pytest.raises(PageNotFoundError):
        Post.page_objects.get_published_page_by_path("non-existint-parent/non-existent-page")


@pytest.mark.django_db
def test_get_non_existent_page_by_path_with_parent(test_page1):
    """Test that the get_published_page_by_path method raises a PageNotFoundError."""
    with pytest.raises(PageNotFoundError):
        Post.page_objects.get_published_page_by_path("test-page1/non-existent-page")


@pytest.mark.django_db
def test_get_valid_page_with_wrong_parent(test_page1, test_page2, test_page3):
    """Test that the get_published_page_by_path method raises a PageNotFoundError."""
    test_page1.parent = test_page2
    test_page1.save()

    assert test_page1 == Post.page_objects.get_published_page_by_path("test-page2/test-page1")
    assert test_page2 == Post.page_objects.get_published_page_by_path("test-page2")
    assert test_page3 == Post.page_objects.get_published_page_by_path("test-page3")

    with pytest.raises(PageNotFoundError):
        Post.page_objects.get_published_page_by_path("test-page3/test-page1")
    with pytest.raises(PageNotFoundError):
        Post.page_objects.get_published_page_by_path("test-page3/test-page2")
    with pytest.raises(PageNotFoundError):
        Post.page_objects.get_published_page_by_path("test-page3/test-page3")
    with pytest.raises(PageNotFoundError):
        Post.page_objects.get_published_page_by_path("test-page1/test-page1")
    with pytest.raises(PageNotFoundError):
        Post.page_objects.get_published_page_by_path("test-page1/test-page2")
    with pytest.raises(PageNotFoundError):
        Post.page_objects.get_published_page_by_path("test-page1/test-page3")
    with pytest.raises(PageNotFoundError):
        Post.page_objects.get_published_page_by_path("test-page2/test-page2")
    with pytest.raises(PageNotFoundError):
        Post.page_objects.get_published_page_by_path("test-page2/test-page3")
    with pytest.raises(PageNotFoundError):
        Post.page_objects.get_published_page_by_path("test-page2/test-page1/test-page3")


@pytest.mark.django_db
def test_get_valid_page_with_wrong_grandparent(test_page1, test_page2, test_page3):
    """Test that the get_published_page_by_path method raises a PageNotFoundError."""
    test_page1.parent = test_page2
    test_page1.save()
    test_page2.parent = test_page3
    test_page2.save()

    assert test_page1 == Post.page_objects.get_published_page_by_path("test-page3/test-page2/test-page1")
    assert test_page2 == Post.page_objects.get_published_page_by_path("test-page3/test-page2")
    assert test_page3 == Post.page_objects.get_published_page_by_path("test-page3")

    with pytest.raises(PageNotFoundError):
        Post.page_objects.get_published_page_by_path("test-page3/test-page1/test-page2")
    with pytest.raises(PageNotFoundError):
        Post.page_objects.get_published_page_by_path("test-page3/test-page2/test-page2")
    with pytest.raises(PageNotFoundError):
        Post.page_objects.get_published_page_by_path("test-page1/test-page2/test-page3")


@pytest.mark.django_db
def test_get_cached_published_posts(settings, monkeypatch, test_post1, test_post2):
    """Test that the get_published_pages method returns the correct pages."""
    # Confirm settings are set according to settings_testing.py
    assert settings.DJPRESS_SETTINGS["CACHE_RECENT_PUBLISHED_POSTS"] is False
    assert settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] == 3

    # Turn on caching and check if the setting is correct
    settings.DJPRESS_SETTINGS["CACHE_RECENT_PUBLISHED_POSTS"] = True
    assert settings.DJPRESS_SETTINGS["CACHE_RECENT_PUBLISHED_POSTS"] is True

    # Mock cache.set and cache.get
    mock_cache_set = Mock()
    mock_cache_get = Mock(return_value=None)
    monkeypatch.setattr(cache, "set", mock_cache_set)
    monkeypatch.setattr(cache, "get", mock_cache_get)

    # First call should set the cache
    assert list(Post.post_objects.get_recent_published_posts()) == [test_post2, test_post1]
    assert mock_cache_set.called

    # Get the arguments passed to cache.set
    args, kwargs = mock_cache_set.call_args

    # Mock cache.get to return the cached value
    mock_cache_get.return_value = [test_post2, test_post1]

    # Second call should read from the cache
    assert list(Post.post_objects.get_recent_published_posts()) == [test_post2, test_post1]
    assert mock_cache_get.called

    # Verify that cache.get was called with the expected key
    cache_key = args[0]  # Assuming the cache key is the first argument to cache.set
    mock_cache_get.assert_called_with(cache_key)


@pytest.mark.django_db
def test_get_cached_future_published_posts(user, settings, mock_timezone_now, monkeypatch, test_post1):
    """Test that the def _get_cached_recent_published_posts method sets the correct timeout.

    This is a complicated test that involves mocking the timezone.now function and the cache.set function.

    The mocking can tell what arguments were passed to cache.set and if the timeout is set correctly.
    """
    # Confirm settings are set according to settings_testing.py
    assert settings.DJPRESS_SETTINGS["CACHE_RECENT_PUBLISHED_POSTS"] is False
    assert settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] == 3

    # Turn on caching and check if the setting is correct
    settings.DJPRESS_SETTINGS["CACHE_RECENT_PUBLISHED_POSTS"] = True
    assert settings.DJPRESS_SETTINGS["CACHE_RECENT_PUBLISHED_POSTS"] is True

    assert mock_timezone_now == timezone.now()

    post_date = mock_timezone_now + timezone.timedelta(hours=2)

    print(f"{mock_timezone_now=}")
    print(f"{post_date=}")

    Post.post_objects.create(
        title="Test Post",
        slug="test-post",
        content="This is a test post.",
        author=user,
        date=post_date,
        status="published",
        post_type="post",
    )

    mock_cache_set = Mock()
    monkeypatch.setattr(cache, "set", mock_cache_set)

    queryset = cache.get(PUBLISHED_POSTS_CACHE_KEY)
    assert queryset is None

    queryset = Post.post_objects.get_recent_published_posts()
    assert len(queryset) == 0

    # Check if cache.set was called
    assert mock_cache_set.called

    # Get the arguments passed to cache.set
    args, kwargs = mock_cache_set.call_args

    # Check if the timeout is correct (should be close to 2 hours)
    expected_timeout = 7200  # 2 hours in seconds

    print(f"{args=}")
    print(f"{kwargs=}")

    actual_timeout = kwargs.get("timeout") or args[2]  # timeout might be a kwarg or the third positional arg
    assert abs(actual_timeout - expected_timeout) < 5  # Allow a small margin of error


@pytest.fixture
def mock_cache(monkeypatch):
    mock_cache_get = Mock()
    mock_cache_set = Mock()
    monkeypatch.setattr(cache, "get", mock_cache_get)
    monkeypatch.setattr(cache, "set", mock_cache_set)
    return mock_cache_get, mock_cache_set


@pytest.mark.django_db
def test_get_recent_published_posts_cache_miss(mock_cache, settings, test_post1, test_post2, test_post3):
    """First time calling the get_recent_published_posts method should result in a cache miss."""
    mock_cache_get, mock_cache_set = mock_cache

    # Simulate cache miss
    mock_cache_get.return_value = None

    # Enable caching
    settings.DJPRESS_SETTINGS["CACHE_RECENT_PUBLISHED_POSTS"] = True

    # Call the method
    queryset = Post.post_objects.get_recent_published_posts()

    # Verify cache.set is called
    assert mock_cache_set.called
    args, kwargs = mock_cache_set.call_args
    cache_key = args[0]
    cached_queryset = args[1]
    timeout = kwargs["timeout"]

    # Verify the queryset is correct
    assert list(queryset) == [test_post3, test_post2, test_post1]
    assert list(cached_queryset) == [test_post3, test_post2, test_post1]


@pytest.mark.django_db
def test_get_recent_published_posts_cache_hit(mock_cache, settings, test_post1, test_post2, test_post3):
    """Test that the get_recent_published_posts method returns the correct posts from the cache."""
    # Confirm settings are set according to settings_testing.py
    assert settings.DJPRESS_SETTINGS["CACHE_RECENT_PUBLISHED_POSTS"] is False
    assert settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] == 3

    mock_cache_get, mock_cache_set = mock_cache

    # Simulate cache hit
    mock_cache_get.return_value = [test_post3, test_post2, test_post1]

    # Enable caching
    settings.DJPRESS_SETTINGS["CACHE_RECENT_PUBLISHED_POSTS"] = True

    # Call the method
    cached_queryset = Post.post_objects.get_recent_published_posts()

    # Verify cache.get is called
    mock_cache_get.assert_called_with(PUBLISHED_POSTS_CACHE_KEY)
    assert list(cached_queryset) == [test_post3, test_post2, test_post1]

    new_queryset = Post.post_objects.get_recent_published_posts()

    # Verify cache.set is not called again
    assert not mock_cache_set.called


@pytest.mark.django_db
def test_get_recent_published_posts_cache_hit_2_posts(mock_cache, settings, test_post1, test_post2):
    """Test that the get_recent_published_posts method returns the correct posts from the cache."""
    # Confirm settings are set according to settings_testing.py
    assert settings.DJPRESS_SETTINGS["CACHE_RECENT_PUBLISHED_POSTS"] is False
    assert settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] == 3

    mock_cache_get, mock_cache_set = mock_cache

    # Simulate cache hit
    mock_cache_get.return_value = [test_post2, test_post1]

    # Enable caching
    settings.DJPRESS_SETTINGS["CACHE_RECENT_PUBLISHED_POSTS"] = True
    settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] = 2

    # Call the method
    cached_queryset = Post.post_objects.get_recent_published_posts()

    # Verify cache.get is called
    mock_cache_get.assert_called_with(PUBLISHED_POSTS_CACHE_KEY)
    assert list(cached_queryset) == [test_post2, test_post1]

    new_queryset = Post.post_objects.get_recent_published_posts()

    # Verify cache.set is not called again
    assert not mock_cache_set.called


@pytest.mark.django_db
def test_get_cached_recent_published_posts_cache_miss(mock_cache, test_post1, test_post2):
    """Test that the _get_cached_recent_published_posts method sets the correct cache key and value."""
    mock_cache_get, mock_cache_set = mock_cache

    # Simulate cache miss
    mock_cache_get.return_value = None

    # Call the method
    queryset = Post.post_objects._get_cached_recent_published_posts()

    # Verify cache.set is called
    assert mock_cache_set.called
    args, kwargs = mock_cache_set.call_args
    cache_key = args[0]
    cached_queryset = args[1]
    timeout = kwargs["timeout"]

    # Verify the queryset is correct
    assert list(queryset) == [test_post2, test_post1]
    assert list(cached_queryset) == [test_post2, test_post1]


@pytest.mark.django_db
def test_get_cached_recent_published_posts_cache_hit(mock_cache, settings, test_post1, test_post2, test_post3):
    assert settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] == 3

    mock_cache_get, mock_cache_set = mock_cache

    # Simulate cache hit
    mock_cache_get.return_value = [test_post3, test_post2, test_post1]

    # Call the method
    cached_queryset = Post.post_objects._get_cached_recent_published_posts()

    # Verify cache.get is called
    mock_cache_get.assert_called_with(PUBLISHED_POSTS_CACHE_KEY)
    assert list(cached_queryset) == [test_post3, test_post2, test_post1]

    # Verify cache.set is not called again
    assert not mock_cache_set.called


@pytest.mark.django_db
def test_get_cached_recent_published_posts_cache_hit_2_posts(mock_cache, settings, test_post1, test_post2):
    assert settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] == 3
    # Change the number of posts to 2
    settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] = 2

    mock_cache_get, mock_cache_set = mock_cache

    # Simulate cache hit
    mock_cache_get.return_value = [test_post2, test_post1]

    # Call the method
    cached_queryset = Post.post_objects._get_cached_recent_published_posts()

    # Verify cache.get is called
    mock_cache_get.assert_called_with(PUBLISHED_POSTS_CACHE_KEY)
    assert list(cached_queryset) == [test_post2, test_post1]

    # Verify cache.set is not called again
    assert not mock_cache_set.called


@pytest.mark.django_db
def test_post_clean_valid_parent(test_page1, test_page2):
    test_page1.parent = test_page2
    test_page1.clean()
    assert test_page1.parent == test_page2


@pytest.mark.django_db
def test_post_clean_self_parent(test_page1):
    test_page1.parent = test_page1
    with pytest.raises(ValidationError) as exc_info:
        test_page1.clean()
    assert "Circular reference detected in page hierarchy." in str(exc_info.value)


@pytest.mark.django_db
def test_post_clean_circular_reference(test_page1, test_page2):
    test_page1.parent = test_page2
    test_page1.clean()
    assert test_page1.parent == test_page2

    # Create a circular reference
    test_page2.parent = test_page1
    with pytest.raises(ValidationError) as exc_info:
        test_page2.clean()
    assert "Circular reference detected in page hierarchy." in str(exc_info.value)


@pytest.mark.django_db
def test_post_clean_circular_reference_extra_level(test_page1, test_page2, test_page3):
    test_page1.parent = test_page2
    test_page1.clean()
    assert test_page1.parent == test_page2

    test_page2.parent = test_page3
    test_page2.clean()
    assert test_page2.parent == test_page3

    # Create a circular reference
    test_page3.parent = test_page1
    with pytest.raises(ValidationError) as exc_info:
        test_page3.clean()
    assert "Circular reference detected in page hierarchy." in str(exc_info.value)


@pytest.mark.django_db
def test_full_page_path_no_parent(test_page1):
    assert test_page1.full_page_path == "test-page1"


@pytest.mark.django_db
def test_get_full_page_path_with_parent(test_page1, test_page2):
    test_page1.parent = test_page2
    assert test_page1.full_page_path == "test-page2/test-page1"


@pytest.mark.django_db
def test_get_full_page_path_with_grandparent(test_page1, test_page2, test_page3):
    test_page1.parent = test_page2
    test_page2.parent = test_page3
    assert test_page1.full_page_path == "test-page3/test-page2/test-page1"


@pytest.mark.django_db
def test_page_get_page_tree_no_children(test_page1, test_page2, test_page3, test_page4):
    expected_tree = [
        {"page": test_page1, "children": []},
        {"page": test_page2, "children": []},
        {"page": test_page3, "children": []},
        {"page": test_page4, "children": []},
    ]
    assert list(Post.page_objects.get_page_tree()) == expected_tree


@pytest.mark.django_db
def test_page_get_page_tree_with_children(test_page1, test_page2, test_page3, test_page4):
    test_page1.parent = test_page2
    test_page1.save()
    test_page3.parent = test_page2
    test_page3.save()

    expected_tree = [
        {
            "page": test_page2,
            "children": [
                {"page": test_page1, "children": []},
                {"page": test_page3, "children": []},
            ],
        },
        {"page": test_page4, "children": []},
    ]
    assert Post.page_objects.get_page_tree() == expected_tree


@pytest.mark.django_db
def test_page_get_page_tree_with_grandchildren(test_page1, test_page2, test_page3, test_page4, test_page5):
    test_page1.parent = test_page2
    test_page1.save()
    test_page3.parent = test_page2
    test_page3.save()
    test_page2.parent = test_page5
    test_page2.save()

    expected_tree = [
        {"page": test_page4, "children": []},
        {
            "page": test_page5,
            "children": [
                {
                    "page": test_page2,
                    "children": [
                        {"page": test_page1, "children": []},
                        {"page": test_page3, "children": []},
                    ],
                },
            ],
        },
    ]
    assert Post.page_objects.get_page_tree() == expected_tree


@pytest.mark.django_db
def test_page_get_page_tree_with_grandchildren_parent_with_future_date(
    test_page1, test_page2, test_page3, test_page4, test_page5
):
    """Test complex page structure.

    test_page5
    ├── test_page2 (future) = should be unpublished
    │   ├── test_page1 = should be unpublished
    │   └── test_page3 = should be unpublished
    test_page4
    """
    test_page1.parent = test_page2
    test_page1.save()
    test_page3.parent = test_page2
    test_page3.save()
    test_page2.parent = test_page5
    test_page2.date = timezone.now() + timezone.timedelta(days=1)
    test_page2.save()

    assert test_page2.is_published is False

    expected_tree = [
        {"page": test_page4, "children": []},
        {"page": test_page5, "children": []},
    ]
    assert Post.page_objects.get_page_tree() == expected_tree


@pytest.mark.django_db
def test_page_get_page_tree_with_grandchildren_parent_with_status_draft(
    test_page1, test_page2, test_page3, test_page4, test_page5
):
    """Test complex page structure.

    test_page5
    ├── test_page2 (future) = should be unpublished
    │   ├── test_page1 = should be unpublished
    │   └── test_page3 = should be unpublished
    test_page4
    """
    test_page1.parent = test_page2
    test_page1.save()
    test_page3.parent = test_page2
    test_page3.save()
    test_page2.parent = test_page5
    test_page2.status = "draft"
    test_page2.save()

    expected_tree = [
        {"page": test_page4, "children": []},
        {"page": test_page5, "children": []},
    ]
    assert Post.page_objects.get_page_tree() == expected_tree


@pytest.mark.django_db
def test_page_order_menu_order(test_page1, test_page2, test_page3, test_page4, test_page5):
    test_page1.menu_order = 1
    test_page1.save()
    test_page2.menu_order = 2
    test_page2.save()
    test_page3.menu_order = 3
    test_page3.save()
    test_page4.menu_order = 4
    test_page4.save()
    test_page5.menu_order = 5
    test_page5.save()

    expected_order = [test_page1, test_page2, test_page3, test_page4, test_page5]

    assert list(Post.page_objects.get_published_pages()) == expected_order


@pytest.mark.django_db
def test_page_order_title(test_page1, test_page2, test_page3, test_page4, test_page5):
    test_page1.menu_order = 1
    test_page1.save()
    test_page2.menu_order = 1
    test_page2.save()
    test_page3.menu_order = 1
    test_page3.save()
    test_page4.menu_order = 1
    test_page4.save()
    test_page5.menu_order = 1
    test_page5.save()

    expected_order = [test_page1, test_page2, test_page3, test_page4, test_page5]

    assert list(Post.page_objects.get_published_pages()) == expected_order


@pytest.mark.django_db
def test_page_is_published_parent_published_page_draft(test_page1, test_page2):
    test_page1.parent = test_page2
    test_page1.save()
    assert test_page1.is_published is True
    assert test_page2.is_published is True

    test_page1.status = "draft"
    test_page1.save()
    assert test_page1.is_published is False
    assert test_page2.is_published is True


@pytest.mark.django_db
def test_page_is_published(test_page1, test_page2, test_page3, test_page4, test_page5):
    # All pages are published
    assert test_page1.is_published is True
    assert test_page2.is_published is True
    assert test_page3.is_published is True
    assert test_page4.is_published is True
    assert test_page5.is_published is True

    # Change test_page1 to be draft - test_page1 will be unpublished
    test_page1.status = "draft"
    test_page1.save()
    assert test_page1.is_published is False

    # Change test_page2 to have test_page1 as the parent - now both will be unpublished
    test_page2.parent = test_page1
    test_page2.save()
    assert test_page1.is_published is False
    assert test_page2.is_published is False

    # Change test_page1 to be published again - test_page1 and the child test_page2 will be published again
    test_page1.status = "published"
    test_page1.save()
    assert test_page1.is_published is True
    assert test_page2.is_published is True

    # Now change test_page2 to draft - test_page1 will still be published, but test_page2 will be unpublished
    test_page2.status = "draft"
    test_page2.save()
    assert test_page1.is_published is True
    assert test_page2.is_published is False

    # Change test_page2 to published - now both will be published again
    test_page2.status = "published"
    test_page2.save()
    assert test_page2.is_published is True
    assert test_page1.is_published is True

    # Change test_page3 to be in the future - test_page3 and the child test_page2 will be unpublished
    test_page3.date = timezone.now() + timezone.timedelta(days=1)
    test_page3.save()
    assert test_page3.is_published is False
    assert test_page2.is_published is True
    assert test_page1.is_published is True

    # Change test_page2 to have test_page3 as the parent - test_page3 and test_page2 will be unpublished and test_page1 will be published
    test_page2.parent = test_page3
    test_page2.save()
    assert test_page3.is_published is False
    assert test_page2.is_published is False
    assert test_page1.is_published is True

    # Change test_page3 to be published again - test_page3 and the child test_page2 will be published
    test_page3.date = timezone.now()
    test_page3.save()
    assert test_page2.is_published is True
    assert test_page3.is_published is True

    # Change test_page3 to have test_page4 as the parent - test_page4, test_page3 and test_page2 will be published
    test_page3.parent = test_page4
    test_page3.save()
    assert test_page3.is_published is True
    assert test_page2.is_published is True
    assert test_page4.is_published is True

    # Change test_page 4 to have test_page5 as the parent - test_page5, test_page4, test_page3 and test_page2 will be published
    test_page4.parent = test_page5
    test_page4.save()
    assert test_page2.is_published is True
    assert test_page3.is_published is True
    assert test_page4.is_published is True
    assert test_page5.is_published is True

    # Change test_page5 to be draft - test_page5, test_page4, test_page3 and test_page2 will be unpublished
    test_page5.status = "draft"
    test_page5.save()
    assert test_page5.is_published is False
    assert test_page3.is_published is False
    assert test_page4.is_published is False
    assert test_page5.is_published is False


@pytest.mark.django_db
def test_page_is_parent(test_page1, test_page2):
    assert test_page1.is_parent is False
    assert test_page2.is_parent is False

    test_page1.parent = test_page2
    test_page1.save()
    assert test_page2.is_parent is True


@pytest.mark.django_db
def test_page_is_child(test_page1, test_page2):
    assert test_page1.is_child is False
    assert test_page2.is_child is False

    test_page1.parent = test_page2
    test_page1.save()
    assert test_page1.is_child is True


@pytest.mark.django_db
def test_parent_page_cant_have_post_child(test_page1, test_post1):
    test_post1.parent = test_page1
    test_post1.save()

    assert test_post1 not in test_page1.children.all()


@pytest.mark.django_db
def test_post_parent_is_none(test_post1, test_page1):
    test_post1.parent = test_page1
    test_post1.save()

    assert test_post1.parent is None


@pytest.mark.django_db
def test_post_get_years(test_post1, test_post2, test_post3):
    # type should be a queryset
    assert isinstance(Post.post_objects.get_years(), QuerySet)
    # Queryset should have 1 item
    assert len(Post.post_objects.get_years()) == 1
    # The item should be the year of the post
    assert Post.post_objects.get_years()[0].year == test_post1.date.year

    test_post2.date = timezone.make_aware(timezone.datetime(2023, 1, 1, 12, 0, 0))
    test_post2.save()

    # Queryset should have 2 items
    assert len(Post.post_objects.get_years()) == 2
    # The items should be the years of the posts
    assert Post.post_objects.get_years()[0].year == test_post2.date.year
    assert Post.post_objects.get_years()[1].year == test_post1.date.year

    test_post3.date = timezone.make_aware(timezone.datetime(2022, 1, 1, 12, 0, 0))
    test_post3.save()

    # Queryset should have 3 items
    assert len(Post.post_objects.get_years()) == 3
    # The items should be the years of the posts
    assert Post.post_objects.get_years()[0].year == test_post3.date.year
    assert Post.post_objects.get_years()[1].year == test_post2.date.year
    assert Post.post_objects.get_years()[2].year == test_post1.date.year

    # Change a post to draft status
    test_post1.status = "draft"
    test_post1.save()

    # Queryset should have 2 items
    assert len(Post.post_objects.get_years()) == 2
    # The items should be the years of the posts
    assert Post.post_objects.get_years()[0].year == test_post3.date.year
    assert Post.post_objects.get_years()[1].year == test_post2.date.year


@pytest.mark.django_db
def test_post_get_months(test_post1, test_post2, test_post3):
    months = Post.post_objects.get_months(test_post1.date.year)

    # type should be a queryset
    assert isinstance(months, QuerySet)
    # Queryset should have 1 item - all three posts are in the same year and month
    assert len(months) == 1
    # The item should be the month of the post
    assert months[0].month == test_post1.date.month

    # Set specific dates for each of the posts
    test_post1.date = timezone.make_aware(timezone.datetime(2022, 1, 1, 12, 0, 0))
    test_post1.save()
    test_post2.date = timezone.make_aware(timezone.datetime(2022, 2, 1, 12, 0, 0))
    test_post2.save()
    test_post3.date = timezone.make_aware(timezone.datetime(2022, 3, 1, 12, 0, 0))
    test_post3.save()

    months = Post.post_objects.get_months(test_post1.date.year)

    # Queryset should have 3 items
    assert len(months) == 3
    # The items should be the months of the posts
    assert months[0].month == test_post1.date.month
    assert months[1].month == test_post2.date.month
    assert months[2].month == test_post3.date.month

    # Change a post to draft status
    test_post1.status = "draft"
    test_post1.save()

    months = Post.post_objects.get_months(test_post1.date.year)

    # Queryset should have 2 items
    assert len(months) == 2
    # The items should be the months of the posts
    assert months[0].month == test_post2.date.month
    assert months[1].month == test_post3.date.month


@pytest.mark.django_db
def test_post_get_days(test_post1, test_post2, test_post3):
    days = Post.post_objects.get_days(test_post1.date.year, test_post1.date.month)

    # type should be a queryset
    assert isinstance(days, QuerySet)
    # Queryset should have 1 item - all three posts are in the same year and month
    assert len(days) == 1

    # Set specific dates for each of the posts
    test_post1.date = timezone.make_aware(timezone.datetime(2022, 1, 1, 12, 0, 0))
    test_post1.save()
    test_post2.date = timezone.make_aware(timezone.datetime(2022, 1, 2, 12, 0, 0))
    test_post2.save()
    test_post3.date = timezone.make_aware(timezone.datetime(2022, 1, 3, 12, 0, 0))
    test_post3.save()

    days = Post.post_objects.get_days(test_post1.date.year, test_post1.date.month)

    # Queryset should have 3 items
    assert len(days) == 3
    # The items should be the days of the posts
    assert days[0].day == test_post1.date.day
    assert days[1].day == test_post2.date.day
    assert days[2].day == test_post3.date.day

    # Change a post to draft status
    test_post1.status = "draft"
    test_post1.save()

    days = Post.post_objects.get_days(test_post1.date.year, test_post1.date.month)

    # Queryset should have 2 items
    assert len(days) == 2
    # The items should be the days of the posts
    assert days[0].day == test_post2.date.day
    assert days[1].day == test_post3.date.day


@pytest.mark.django_db
def test_get_year_last_modified(test_post1, test_post2, test_post3):
    # Should match the modified date of the last post in the list - i.e. most recent post
    assert Post.post_objects.get_year_last_modified(test_post1.date.year) == test_post3.modified_date

    # Change test_post3 to draft and it should now match test_post2
    test_post3.status = "draft"
    test_post3.save()
    assert Post.post_objects.get_year_last_modified(test_post1.date.year) == test_post2.modified_date

    # Changetest_post2 to future date and it should now match test_post1
    test_post2.date = timezone.now() + timezone.timedelta(days=1)
    test_post2.save()
    assert Post.post_objects.get_year_last_modified(test_post1.date.year) == test_post1.modified_date


@pytest.mark.django_db
def test_get_month_last_modified(test_post1, test_post2, test_post3):
    # Should match the modified date of the last post in the list - i.e. most recent post
    assert (
        Post.post_objects.get_month_last_modified(test_post1.date.year, test_post1.date.month)
        == test_post3.modified_date
    )

    # Change test_post3 to draft and it should now match test_post2
    test_post3.status = "draft"
    test_post3.save()
    assert (
        Post.post_objects.get_month_last_modified(test_post1.date.year, test_post1.date.month)
        == test_post2.modified_date
    )

    # Changetest_post2 to future date and it should now match test_post1
    test_post2.date = timezone.now() + timezone.timedelta(days=1)
    test_post2.save()
    assert (
        Post.post_objects.get_month_last_modified(test_post1.date.year, test_post1.date.month)
        == test_post1.modified_date
    )


@pytest.mark.django_db
def test_get_day_last_modified(test_post1, test_post2, test_post3):
    # Should match the modified date of the last post in the list - i.e. most recent post
    assert (
        Post.post_objects.get_day_last_modified(test_post1.date.year, test_post1.date.month, test_post1.date.day)
        == test_post3.modified_date
    )

    # Change test_post3 to draft and it should now match test_post2
    test_post3.status = "draft"
    test_post3.save()
    assert (
        Post.post_objects.get_day_last_modified(test_post1.date.year, test_post1.date.month, test_post1.date.day)
        == test_post2.modified_date
    )

    # Changetest_post2 to future date and it should now match test_post1
    test_post2.date = timezone.now() + timezone.timedelta(days=1)
    test_post2.save()
    assert (
        Post.post_objects.get_day_last_modified(test_post1.date.year, test_post1.date.month, test_post1.date.day)
        == test_post1.modified_date
    )


@pytest.mark.django_db
def test_get_published_posts_by_tags(test_post1, test_post2, test_post3, tag1, tag2, tag3):
    test_post1.tags.add(tag1)
    assert Post.post_objects.get_published_posts_by_tags([tag1.slug]).count() == 1
    assert Post.post_objects.get_published_posts_by_tags([tag2.slug]).count() == 0
    assert Post.post_objects.get_published_posts_by_tags([tag1.slug, tag2.slug]).count() == 0
    assert Post.post_objects.get_published_posts_by_tags([tag1.slug, tag2.slug, tag3.slug]).count() == 0

    test_post2.tags.add(tag2)
    assert Post.post_objects.get_published_posts_by_tags([tag1.slug]).count() == 1
    assert Post.post_objects.get_published_posts_by_tags([tag2.slug]).count() == 1
    assert Post.post_objects.get_published_posts_by_tags([tag1.slug, tag2.slug]).count() == 0
    assert Post.post_objects.get_published_posts_by_tags([tag1.slug, tag2.slug, tag3.slug]).count() == 0

    test_post1.tags.add(tag2)
    assert Post.post_objects.get_published_posts_by_tags([tag1.slug]).count() == 1
    assert Post.post_objects.get_published_posts_by_tags([tag2.slug]).count() == 2
    assert Post.post_objects.get_published_posts_by_tags([tag1.slug, tag2.slug]).count() == 1
    assert Post.post_objects.get_published_posts_by_tags([tag1.slug, tag2.slug, tag3.slug]).count() == 0

    test_post2.tags.add(tag1)
    assert Post.post_objects.get_published_posts_by_tags([tag1.slug]).count() == 2
    assert Post.post_objects.get_published_posts_by_tags([tag2.slug]).count() == 2
    assert Post.post_objects.get_published_posts_by_tags([tag1.slug, tag2.slug]).count() == 2
    assert Post.post_objects.get_published_posts_by_tags([tag1.slug, tag2.slug, tag3.slug]).count() == 0

    test_post3.tags.add(tag1)
    assert Post.post_objects.get_published_posts_by_tags([tag1.slug]).count() == 3
    assert Post.post_objects.get_published_posts_by_tags([tag2.slug]).count() == 2
    assert Post.post_objects.get_published_posts_by_tags([tag1.slug, tag2.slug]).count() == 2
    assert Post.post_objects.get_published_posts_by_tags([tag1.slug, tag2.slug, tag3.slug]).count() == 0

    test_post3.tags.add(tag2)
    assert Post.post_objects.get_published_posts_by_tags([tag1.slug]).count() == 3
    assert Post.post_objects.get_published_posts_by_tags([tag2.slug]).count() == 3
    assert Post.post_objects.get_published_posts_by_tags([tag1.slug, tag2.slug]).count() == 3
    assert Post.post_objects.get_published_posts_by_tags([tag1.slug, tag2.slug, tag3.slug]).count() == 0

    test_post3.tags.add(tag3)
    assert Post.post_objects.get_published_posts_by_tags([tag1.slug]).count() == 3
    assert Post.post_objects.get_published_posts_by_tags([tag2.slug]).count() == 3
    assert Post.post_objects.get_published_posts_by_tags([tag1.slug, tag2.slug]).count() == 3
    assert Post.post_objects.get_published_posts_by_tags([tag1.slug, tag2.slug, tag3.slug]).count() == 1

    test_post1.tags.add(tag3)
    assert Post.post_objects.get_published_posts_by_tags([tag1.slug]).count() == 3
    assert Post.post_objects.get_published_posts_by_tags([tag2.slug]).count() == 3
    assert Post.post_objects.get_published_posts_by_tags([tag1.slug, tag2.slug]).count() == 3
    assert Post.post_objects.get_published_posts_by_tags([tag1.slug, tag2.slug, tag3.slug]).count() == 2


@pytest.mark.django_db
def test_get_published_posts_by_tags_missing_tag(test_post1, test_post2, tag1, tag2):
    test_post1.tags.add(tag1)
    test_post1.tags.add(tag2)
    test_post2.tags.add(tag1)
    test_post2.tags.add(tag2)

    assert Post.post_objects.get_published_posts_by_tags([tag1.slug]).count() == 2
    assert Post.post_objects.get_published_posts_by_tags([tag2.slug]).count() == 2
    assert Post.post_objects.get_published_posts_by_tags([tag1.slug, tag2.slug]).count() == 2

    assert Post.post_objects.get_published_posts_by_tags(["invalid-tag"]).count() == 0
    assert Post.post_objects.get_published_posts_by_tags([tag1.slug, "invalid-tag"]).count() == 0
    assert Post.post_objects.get_published_posts_by_tags([tag1.slug, tag2.slug, "invalid-tag"]).count() == 0


@pytest.mark.django_db
def test_max_tags_per_query(settings, test_post1, test_post2, test_post3, tag1, tag2, tag3):
    test_post1.tags.add(tag1)
    test_post1.tags.add(tag2)
    test_post1.tags.add(tag3)
    assert Post.post_objects.get_published_posts_by_tags([tag1.slug]).count() == 1
    assert Post.post_objects.get_published_posts_by_tags([tag2.slug]).count() == 1
    assert Post.post_objects.get_published_posts_by_tags([tag3.slug]).count() == 1
    assert Post.post_objects.get_published_posts_by_tags([tag1.slug, tag2.slug]).count() == 1
    assert Post.post_objects.get_published_posts_by_tags([tag1.slug, tag2.slug, tag3.slug]).count() == 1

    settings.DJPRESS_SETTINGS["MAX_TAGS_PER_QUERY"] = 2
    assert Post.post_objects.get_published_posts_by_tags([tag1.slug, tag2.slug]).count() == 1
    assert Post.post_objects.get_published_posts_by_tags([tag1.slug, tag3.slug]).count() == 1
    assert Post.post_objects.get_published_posts_by_tags([tag2.slug, tag3.slug]).count() == 1
    assert Post.post_objects.get_published_posts_by_tags([tag1.slug, tag2.slug, tag3.slug]).count() == 0
