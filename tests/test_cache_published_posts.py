import pytest

from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils import timezone

from djpress.conf import settings as djpress_settings
from djpress.models import Post
from djpress.models.post import PUBLISHED_POSTS_CACHE_KEY


@pytest.mark.django_db
def test_get_cached_content(user, settings):
    # Confirm the settings in settings_testing.py
    assert djpress_settings.CACHE_RECENT_PUBLISHED_POSTS is False
    assert settings.DJPRESS_SETTINGS["CACHE_RECENT_PUBLISHED_POSTS"] is False

    # Create some test content
    Post.post_objects.create(
        title="Content 1",
        content="This is a test post.",
        author=user,
        status="published",
        post_type="post",
    )
    Post.post_objects.create(
        title="Content 2",
        content="This is another test post.",
        author=user,
        status="published",
        post_type="post",
    )

    # Call the _get_cached_recent_published_content method - this forces the cache to be set, regardless of settings
    queryset = Post.post_objects._get_cached_recent_published_posts()

    # Assert that the queryset is cached
    cached_queryset = cache.get(PUBLISHED_POSTS_CACHE_KEY)
    assert cached_queryset is not None
    assert len(queryset) == 2
    assert len(cached_queryset) == 2

    # Assert that subsequent calls retrieve the queryset from cache
    queryset2 = Post.post_objects._get_cached_recent_published_posts()
    assert list(queryset2) == list(cached_queryset)


@pytest.mark.django_db
def test_cache_invalidation_on_save(user):
    # Confirm the settings in settings_testing.py
    assert djpress_settings.CACHE_RECENT_PUBLISHED_POSTS is False

    # Create some test content
    content = Post.post_objects.create(
        title="Content 1",
        content="This is a test post.",
        author=user,
        status="published",
        post_type="post",
    )

    # Call the _get_cached_recent_published_content method - this forces the cache to be set, regardless of settings
    queryset = Post.post_objects._get_cached_recent_published_posts()

    # Assert that the queryset is cached
    cached_queryset = cache.get(PUBLISHED_POSTS_CACHE_KEY)
    assert cached_queryset is not None
    assert len(queryset) == 1

    # Modify the content and save it
    content.title = "Updated Content 1"
    content.save()

    # Assert that the cache is invalidated
    cached_queryset = cache.get(PUBLISHED_POSTS_CACHE_KEY)
    assert cached_queryset is None

    # Call the get_cached_published_content method again
    queryset2 = Post.post_objects._get_cached_recent_published_posts()

    # Assert that the queryset is cached again with the updated data
    cached_queryset2 = cache.get(PUBLISHED_POSTS_CACHE_KEY)
    assert cached_queryset2 is not None
    assert len(queryset2) == 1
    assert queryset2[0].title == "Updated Content 1"


@pytest.mark.django_db
def test_cache_invalidation_on_delete(user):
    # Confirm the settings in settings_testing.py
    assert djpress_settings.CACHE_RECENT_PUBLISHED_POSTS is False

    # Create some test content
    content = Post.post_objects.create(
        title="Content 1",
        content="This is a test post.",
        author=user,
        status="published",
        post_type="post",
    )

    # Call the _get_cached_recent_published_content method - this forces the cache to be set, regardless of settings
    queryset = Post.post_objects._get_cached_recent_published_posts()

    # Assert that the queryset is cached
    cached_queryset = cache.get(PUBLISHED_POSTS_CACHE_KEY)
    assert cached_queryset is not None
    assert len(queryset) == 1

    # Delete the category
    content.delete()

    # Assert that the cache is invalidated
    cached_queryset = cache.get(PUBLISHED_POSTS_CACHE_KEY)
    assert cached_queryset is None

    # Call the get_cached_published_content method again
    queryset2 = Post.post_objects._get_cached_recent_published_posts()

    # Assert that the queryset is cached again with the updated data
    cached_queryset2 = cache.get(PUBLISHED_POSTS_CACHE_KEY)
    assert cached_queryset2 is not None
    assert len(queryset2) == 0


@pytest.mark.django_db
def test_cache_get_recent_published_posts(user, settings):
    """Test that the get_recent_published_posts method returns the correct posts."""

    # Confirm settings are set according to settings_testing.py
    assert settings.DJPRESS_SETTINGS["CACHE_RECENT_PUBLISHED_POSTS"] is False
    assert settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] == 3

    # Enable the posts cache
    settings.DJPRESS_SETTINGS["CACHE_RECENT_PUBLISHED_POSTS"] = True
    assert settings.DJPRESS_SETTINGS["CACHE_RECENT_PUBLISHED_POSTS"] is True

    # Create some published posts
    post1 = Post.objects.create(title="Post 1", status="published", author=user, content="Test post")
    post2 = Post.objects.create(title="Post 2", status="published", author=user, content="Test post")
    post3 = Post.objects.create(title="Post 3", status="published", author=user, content="Test post")

    # Call the method being tested
    recent_posts = Post.post_objects.get_recent_published_posts()

    # Assert that the correct posts are returned
    assert list(recent_posts) == [post3, post2, post1]

    # Check that all posts are cached
    cached_queryset = cache.get(PUBLISHED_POSTS_CACHE_KEY)
    assert cached_queryset is not None
    assert list(cached_queryset) == [post3, post2, post1]

    # Test case 2: Limit the number of posts returned
    settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] = 2
    assert settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] == 2

    # Call the method being tested again
    recent_posts_2 = Post.post_objects.get_recent_published_posts()

    # # Assert that the correct posts are returned
    assert list(recent_posts_2) == [post3, post2]
    assert post1 not in recent_posts_2

    # Check that all posts are cached
    cached_queryset = cache.get(PUBLISHED_POSTS_CACHE_KEY)
    assert cached_queryset is not None
    assert list(cached_queryset) == [post3, post2]


@pytest.mark.django_db
def test_cache_get_recent_published_posts_future_post(user, settings):
    """Test that the get_recent_published_posts method returns the correct posts when there are future posts."""

    # Confirm settings are set according to settings_testing.py
    assert settings.DJPRESS_SETTINGS["CACHE_RECENT_PUBLISHED_POSTS"] is False
    assert settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] == 3

    # Enable the posts cache
    settings.DJPRESS_SETTINGS["CACHE_RECENT_PUBLISHED_POSTS"] = True
    assert settings.DJPRESS_SETTINGS["CACHE_RECENT_PUBLISHED_POSTS"] is True

    # Create some published posts
    post1 = Post.objects.create(title="Post 1", status="published", author=user, content="Test post")
    post2 = Post.objects.create(title="Post 2", status="published", author=user, content="Test post")

    # Call the method being tested
    recent_posts = Post.post_objects.get_recent_published_posts()

    # Assert that the correct posts are returned
    assert list(recent_posts) == [post2, post1]
