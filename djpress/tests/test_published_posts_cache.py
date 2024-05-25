import pytest

from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils import timezone

from djpress.models import Post
from djpress.models.post import PUBLISHED_POSTS_CACHE_KEY


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()


@pytest.mark.django_db
def test_get_cached_content():
    user = User.objects.create_user(username="testuser", password="testpass")
    # Create some test content
    Post.post_objects.create(
        title="Content 1",
        content="This is a test post.",
        author=user,
        status="published",
        post_type="post",
        date=timezone.now(),
    )
    Post.post_objects.create(
        title="Content 2",
        content="This is another test post.",
        author=user,
        status="published",
        post_type="post",
        date=timezone.now(),
    )

    # Call the _get_cached_recent_published_content method
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
def test_cache_invalidation_on_save():
    user = User.objects.create_user(username="testuser", password="testpass")
    # Create some test content
    content = Post.post_objects.create(
        title="Content 1",
        content="This is a test post.",
        author=user,
        status="published",
        post_type="post",
        date=timezone.now(),
    )

    # Call the get_cached_published_content method
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
def test_cache_invalidation_on_delete():
    user = User.objects.create_user(username="testuser", password="testpass")
    # Create some test content
    content = Post.post_objects.create(
        title="Content 1",
        content="This is a test post.",
        author=user,
        status="published",
        post_type="post",
        date=timezone.now(),
    )

    # Call the get_cached_published_content method
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
