# test_category_cache.py

import pytest

from django.core.cache import cache

from djpress.conf import settings
from djpress.models import Category
from djpress.models.category import CATEGORY_CACHE_KEY


@pytest.mark.django_db
def test_get_cached_categories():
    # Confirm the settings in settings_testing.py
    assert settings.CACHE_CATEGORIES is True

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
    # Confirm the settings in settings_testing.py
    assert settings.CACHE_CATEGORIES is True

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
    # Confirm the settings in settings_testing.py
    assert settings.CACHE_CATEGORIES is True

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


@pytest.mark.django_db
def test_cache_get_category_by_slug():
    """Test that the get_category_by_slug method returns the correct category."""
    # Confirm the settings in settings_testing.py
    assert settings.CACHE_CATEGORIES is True

    category1 = Category.objects.create(name="Category 1", slug="category-1")
    category2 = Category.objects.create(name="Category 2", slug="category-2")

    category = Category.objects.get_category_by_slug("category-1")

    assert category == category1
    assert not category == category2


@pytest.mark.django_db
def test_cache_get_category_by_slug_not_in_cache():
    """Test that the get_category_by_slug method returns the correct category."""
    # Confirm the settings in settings_testing.py
    assert settings.CACHE_CATEGORIES is True

    category1 = Category.objects.create(name="Category 1", slug="category-1")
    category2 = Category.objects.create(name="Category 2", slug="category-2")

    # Call the get_cached_categories method
    queryset = Category.objects._get_cached_categories()

    cached_queryset = cache.get(CATEGORY_CACHE_KEY)

    assert cached_queryset is not None
    assert category1 in cached_queryset
    assert category2 in cached_queryset

    cache.delete(CATEGORY_CACHE_KEY)
    cached_queryset = cache.get(CATEGORY_CACHE_KEY)

    assert cached_queryset is None

    category = Category.objects.get_category_by_slug("category-1")

    assert category == category1
    assert not category == category2


@pytest.mark.django_db
def test_cache_get_category_by_slug_not_exists():
    """Test that the get_category_by_slug method returns None when the category does not exist."""
    # Confirm the settings in settings_testing.py
    assert settings.CACHE_CATEGORIES is True

    with pytest.raises(ValueError) as excinfo:
        _ = Category.objects.get_category_by_slug("non-existent-category")
    assert "Category not found" in str(excinfo.value)
