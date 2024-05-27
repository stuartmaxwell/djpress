# test_category_cache.py

import pytest
from django.core.cache import cache
from djpress.models import Category
from djpress.models.category import CATEGORY_CACHE_KEY


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()


@pytest.mark.django_db
def test_get_cached_categories():
    # Create some test categories
    Category.objects.create(name="Category 1")
    Category.objects.create(name="Category 2")

    # Call the get_cached_categories method
    queryset = Category.objects._get_cached_categories()

    # Assert that the queryset is cached
    cached_queryset = cache.get(CATEGORY_CACHE_KEY)
    assert cached_queryset is not None
    assert len(queryset) == 2
    assert len(cached_queryset) == 2

    # Assert that subsequent calls retrieve the queryset from cache
    queryset2 = Category.objects._get_cached_categories()
    assert list(queryset2) == list(cached_queryset)


@pytest.mark.django_db
def test_cache_invalidation_on_save():
    # Create a test category
    category = Category.objects.create(name="Category 1")

    # Call the get_cached_categories method
    queryset = Category.objects._get_cached_categories()

    # Assert that the queryset is cached
    cached_queryset = cache.get(CATEGORY_CACHE_KEY)
    assert cached_queryset is not None
    assert len(queryset) == 1

    # Modify the category and save it
    category.name = "Updated Category"
    category.save()

    # Assert that the cache is invalidated
    cached_queryset = cache.get(CATEGORY_CACHE_KEY)
    assert cached_queryset is None

    # Call the get_cached_categories method again
    queryset2 = Category.objects._get_cached_categories()

    # Assert that the queryset is cached again with the updated data
    cached_queryset2 = cache.get(CATEGORY_CACHE_KEY)
    assert cached_queryset2 is not None
    assert len(queryset2) == 1
    assert queryset2[0].name == "Updated Category"


@pytest.mark.django_db
def test_cache_invalidation_on_delete():
    # Create a test category
    category = Category.objects.create(name="Category 1")

    # Call the get_cached_categories method
    queryset = Category.objects._get_cached_categories()

    # Assert that the queryset is cached
    cached_queryset = cache.get(CATEGORY_CACHE_KEY)
    assert cached_queryset is not None
    assert len(queryset) == 1

    # Delete the category
    category.delete()

    # Assert that the cache is invalidated
    cached_queryset = cache.get(CATEGORY_CACHE_KEY)
    assert cached_queryset is None

    # Call the get_cached_categories method again
    queryset2 = Category.objects._get_cached_categories()

    # Assert that the queryset is cached again with the updated data
    cached_queryset2 = cache.get(CATEGORY_CACHE_KEY)
    assert cached_queryset2 is not None
    assert len(queryset2) == 0
