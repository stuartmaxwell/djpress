import pytest

from django.utils import timezone
from unittest.mock import Mock
from djpress.models import Category, Post
from django.core.cache import cache

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
def test_post_methods(test_post1, test_post2, category1, category2):
    assert Post.post_objects.all().count() == 2
    assert Post.post_objects.get_published_post_by_slug("test-post1").title == "Test Post1"
    assert Post.post_objects.get_published_posts_by_category(category1).count() == 1


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
    assert Post.post_objects.all().count() == 2
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
def test_post_permalink(user, settings):
    post = Post(
        title="Test Post",
        slug="test-post",
        content="This is a test post.",
        author=user,
        date=timezone.make_aware(timezone.datetime(2024, 1, 1)),
        status="published",
        post_type="post",
    )

    # Confirm the post prefix and permalink settings are set according to settings_testing.py
    assert settings.DJPRESS_SETTINGS["POST_PREFIX"] == "test-posts"
    assert post.permalink == "test-posts/test-post"

    # Test with no post prefix
    settings.DJPRESS_SETTINGS["POST_PREFIX"] = ""
    assert post.permalink == "test-post"

    # Test with text, year, month, day post prefix
    settings.DJPRESS_SETTINGS["POST_PREFIX"] = "test-posts/{{ year }}/{{ month }}/{{ day }}"
    assert post.permalink == "test-posts/2024/01/01/test-post"

    # Test with text, year, month post prefix
    settings.DJPRESS_SETTINGS["POST_PREFIX"] = "test-posts/{{ year }}/{{ month }}"
    assert post.permalink == "test-posts/2024/01/test-post"

    # Test with text, year post prefix
    settings.DJPRESS_SETTINGS["POST_PREFIX"] = "test-posts/{{ year }}"
    assert post.permalink == "test-posts/2024/test-post"

    # Test with year, month, day post prefix
    settings.DJPRESS_SETTINGS["POST_PREFIX"] = "{{ year }}/{{ month }}/{{ day }}"
    assert post.permalink == "2024/01/01/test-post"

    # Test with year, month post prefix
    settings.DJPRESS_SETTINGS["POST_PREFIX"] = "{{ year }}/{{ month }}"
    assert post.permalink == "2024/01/test-post"

    # Test with year post prefix
    settings.DJPRESS_SETTINGS["POST_PREFIX"] = "{{ year }}"
    assert post.permalink == "2024/test-post"


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
def test_page_permalink(user):
    page = Post(
        title="Test Page",
        slug="test-page",
        content="This is a test page.",
        author=user,
        date=timezone.now(),
        status="published",
        post_type="page",
    )

    assert page.permalink == "test-page"


@pytest.mark.django_db
def test_get_recent_published_posts(user, settings):
    """Test that the get_recent_published_posts method returns the correct posts."""
    # Confirm settings are set according to settings_testing.py
    assert settings.DJPRESS_SETTINGS["CACHE_RECENT_PUBLISHED_POSTS"] is False
    assert settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] == 3

    # Create some published posts
    post1 = Post.objects.create(title="Post 1", status="published", author=user)
    post2 = Post.objects.create(title="Post 2", status="published", author=user)
    post3 = Post.objects.create(title="Post 3", status="published", author=user)

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
def test_get_published_pages(test_page1, test_page2):
    """Test that the get_published_pages method returns the correct pages."""
    assert list(Post.page_objects.get_published_pages()) == [test_page2, test_page1]


@pytest.mark.django_db
def test_get_published_page_by_path(test_page1: Post):
    """Test that the get_published_page_by_path method returns the correct page."""

    # Test case 1: pages can only be at the top level
    page_path = f"test-pages/{test_page1.slug}"
    with pytest.raises(expected_exception=ValueError):
        Post.page_objects.get_published_page_by_path(page_path)

    # Test case 2: pages at the top level
    page_path: str = test_page1.slug
    assert test_page1 == Post.page_objects.get_published_page_by_path(page_path)

    # Test case 3: pages doesn't exist
    page_path = "non-existent-page"
    with pytest.raises(expected_exception=PageNotFoundError):
        Post.page_objects.get_published_page_by_path(page_path)


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
def test_get_cached_future_published_posts(user, settings, mock_timezone_now, monkeypatch):
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

    Post.post_objects.create(
        title="Test Post",
        slug="test-post",
        content="This is a test post.",
        author=user,
        date=mock_timezone_now + timezone.timedelta(hours=2),
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
