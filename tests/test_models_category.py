import pytest

from djpress.models import Category
from django.utils.text import slugify

from djpress.conf import settings


@pytest.mark.django_db
def test_category_model():
    category = Category.objects.create(name="Test Category", slug="test-category")
    assert category.name == "Test Category"
    assert category.slug == "test-category"
    assert str(category) == "Test Category"


@pytest.mark.django_db
def test_category_save_slug_generation():
    """Test that the slug is correctly generated when saving a Category."""
    category = Category(name="Test Category")
    category.save()

    assert category.slug == slugify("Test Category")


@pytest.mark.django_db
def test_category_save_slug_uniqueness():
    """Test that an error is raised when trying to save a Category with a duplicate slug."""
    category1 = Category(name="Test Category")
    category1.save()

    category2 = Category(name="Test Category")

    with pytest.raises(ValueError) as excinfo:
        category2.save()

    assert (
        str(excinfo.value)
        == f"A category with the slug {category2.slug} already exists."
    )


@pytest.mark.django_db
def test_category_save_invalid_name():
    """Test that an error is raised when trying to save a Category with an invalid name."""
    category = Category(name="-")

    with pytest.raises(ValueError) as excinfo:
        category.save()

    assert str(excinfo.value) == "Invalid name. Unable to generate a valid slug."


@pytest.mark.django_db
def test_category_slug_auto_generation():
    # Test case 1: Slug auto-generated when not provided
    category1 = Category.objects.create(name="Test Category")
    assert category1.slug == slugify(category1.name)

    # Test case 2: Slug not overridden when provided
    category2 = Category.objects.create(name="Another Category", slug="custom-slug")
    assert category2.slug == "custom-slug"

    # Test case 3: Slug auto-generated with special characters
    category3 = Category.objects.create(name="Special !@#$%^&*() Category")
    assert category3.slug == "special-category"

    # Test case 4: Slug auto-generated with non-ASCII characters
    category4 = Category.objects.create(name="Non-ASCII áéíóú Category")
    assert category4.slug == "non-ascii-aeiou-category"

    # Test case 5: Slug auto-generated with leading/trailing hyphens
    category5 = Category.objects.create(name="--Leading/Trailing Hyphens--")
    assert category5.slug == "leadingtrailing-hyphens"

    # Test case 6: Raise ValueError for invalid name
    with pytest.raises(ValueError) as exc_info:
        Category.objects.create(name="!@#$%^&*()")
    assert str(exc_info.value) == "Invalid name. Unable to generate a valid slug."


@pytest.mark.django_db
def test_get_categories_cache_enabled():
    """Test that the get_categories method returns the correct categories."""
    category1 = Category.objects.create(name="Category 1")
    category2 = Category.objects.create(name="Category 2")
    category3 = Category.objects.create(name="Category 3")

    # Confirm the settings in settings_testing.py
    assert settings.CACHE_CATEGORIES is True

    categories = Category.objects.get_categories()

    assert list(categories) == [category1, category2, category3]


@pytest.mark.django_db
def test_get_categories_cache_disabled():
    """Test that the get_categories method returns the correct categories."""
    category1 = Category.objects.create(name="Category 1")
    category2 = Category.objects.create(name="Category 2")
    category3 = Category.objects.create(name="Category 3")

    # Confirm the settings in settings_testing.py
    assert settings.CACHE_CATEGORIES is True

    settings.set("CACHE_CATEGORIES", False)
    assert settings.CACHE_CATEGORIES is False
    categories = Category.objects.get_categories()

    assert list(categories) == [category1, category2, category3]

    # Set back to default
    settings.set("CACHE_CATEGORIES", True)


@pytest.mark.django_db
def test_get_category_by_slug_cache_enabled():
    """Test that the get_category_by_slug method returns the correct category."""
    # Confirm the settings in settings_testing.py
    assert settings.CACHE_CATEGORIES is True

    category1 = Category.objects.create(name="Category 1", slug="category-1")
    category2 = Category.objects.create(name="Category 2", slug="category-2")

    category = Category.objects.get_category_by_slug("category-1")

    assert category == category1
    assert not category == category2


@pytest.mark.django_db
def test_get_category_by_slug_cache_disabled():
    """Test that the get_category_by_slug method returns the correct category."""
    # Confirm the settings in settings_testing.py
    assert settings.CACHE_CATEGORIES is True

    settings.set("CACHE_CATEGORIES", False)
    assert settings.CACHE_CATEGORIES is False

    category1 = Category.objects.create(name="Category 1", slug="category-1")
    category2 = Category.objects.create(name="Category 2", slug="category-2")

    category = Category.objects.get_category_by_slug("category-1")

    assert category == category1
    assert not category == category2

    # Set back to default
    settings.set("CACHE_CATEGORIES", True)


@pytest.mark.django_db
def test_get_category_by_slug_not_exists():
    """Test that the get_category_by_slug method returns None when the category does not exist."""
    # Confirm the settings in settings_testing.py
    assert settings.CACHE_CATEGORIES is True

    settings.set("CACHE_CATEGORIES", False)
    assert settings.CACHE_CATEGORIES is False

    with pytest.raises(ValueError) as excinfo:
        _ = Category.objects.get_category_by_slug("non-existent-category")
    assert "Category not found" in str(excinfo.value)

    # Set back to default
    settings.set("CACHE_CATEGORIES", True)


@pytest.mark.django_db
def test_category_permalink():
    """Test that the permalink property returns the correct URL."""
    # Confirm the settings in settings_testing.py
    assert settings.CACHE_CATEGORIES is True
    assert settings.CATEGORY_PATH_ENABLED is True
    assert settings.CATEGORY_PATH == "test-url-category"

    category = Category.objects.create(name="Test Category", slug="test-category")

    assert category.permalink == "test-url-category/test-category"

    settings.set("CATEGORY_PATH_ENABLED", False)
    settings.set("CATEGORY_PATH", "")

    assert category.permalink == "test-category"

    # Set back to default
    settings.set("CATEGORY_PATH_ENABLED", True)
    settings.set("CATEGORY_PATH", "test-url-category")
