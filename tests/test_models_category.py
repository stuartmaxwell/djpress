import pytest

from djpress.models import Category
from django.utils.text import slugify


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
