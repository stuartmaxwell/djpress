import pytest

from djpress.models import Category
from django.utils.text import slugify
from django.utils import timezone


@pytest.mark.django_db
def test_category_model():
    category = Category.objects.create(title="Test Category", slug="test-category")
    assert category.title == "Test Category"
    assert category.slug == "test-category"
    assert str(category) == "Test Category"


@pytest.mark.django_db
def test_category_save_slug_generation():
    """Test that the slug is correctly generated when saving a Category."""
    category = Category(title="Test Category")
    category.save()

    assert category.slug == slugify("Test Category")


@pytest.mark.django_db
def test_category_save_slug_uniqueness():
    """Test that an error is raised when trying to save a Category with a duplicate slug."""
    category1 = Category(title="Test Category")
    category1.save()

    category2 = Category(title="Test Category")

    with pytest.raises(ValueError) as excinfo:
        category2.save()

    assert str(excinfo.value) == f"A category with the slug {category2.slug} already exists."


@pytest.mark.django_db
def test_category_save_invalid_name():
    """Test that an error is raised when trying to save a Category with an invalid name."""
    category = Category(title="-")

    with pytest.raises(ValueError) as excinfo:
        category.save()

    assert str(excinfo.value) == "Invalid title. Unable to generate a valid slug."


@pytest.mark.django_db
def test_category_slug_auto_generation():
    # Test case 1: Slug auto-generated when not provided
    category1 = Category.objects.create(title="Test Category")
    assert category1.slug == slugify(category1.title)

    # Test case 2: Slug not overridden when provided
    category2 = Category.objects.create(title="Another Category", slug="custom-slug")
    assert category2.slug == "custom-slug"

    # Test case 3: Slug auto-generated with special characters
    category3 = Category.objects.create(title="Special !@#$%^&*() Category")
    assert category3.slug == "special-category"

    # Test case 4: Slug auto-generated with non-ASCII characters
    category4 = Category.objects.create(title="Non-ASCII áéíóú Category")
    assert category4.slug == "non-ascii-aeiou-category"

    # Test case 5: Slug auto-generated with leading/trailing hyphens
    category5 = Category.objects.create(title="--Leading/Trailing Hyphens--")
    assert category5.slug == "leadingtrailing-hyphens"

    # Test case 6: Raise ValueError for invalid title
    with pytest.raises(ValueError) as exc_info:
        Category.objects.create(title="!@#$%^&*()")
    assert str(exc_info.value) == "Invalid title. Unable to generate a valid slug."


@pytest.mark.django_db
def test_get_categories_cache_enabled(settings):
    """Test that the get_categories method returns the correct categories."""
    category1 = Category.objects.create(title="Category 1")
    category2 = Category.objects.create(title="Category 2")
    category3 = Category.objects.create(title="Category 3")

    # Confirm the settings in settings_testing.py
    assert settings.DJPRESS_SETTINGS["CACHE_CATEGORIES"] is True

    categories = Category.objects.get_categories()

    assert list(categories) == [category1, category2, category3]


@pytest.mark.django_db
def test_get_categories_cache_disabled(settings):
    """Test that the get_categories method returns the correct categories."""
    category1 = Category.objects.create(title="Category 1")
    category2 = Category.objects.create(title="Category 2")
    category3 = Category.objects.create(title="Category 3")

    # Confirm the settings in settings_testing.py
    assert settings.DJPRESS_SETTINGS["CACHE_CATEGORIES"] is True

    settings.DJPRESS_SETTINGS["CACHE_CATEGORIES"] = False
    assert settings.DJPRESS_SETTINGS["CACHE_CATEGORIES"] is False
    categories = Category.objects.get_categories()

    assert list(categories) == [category1, category2, category3]


@pytest.mark.django_db
def test_get_category_by_slug_cache_enabled(settings):
    """Test that the get_category_by_slug method returns the correct category."""
    # Confirm the settings in settings_testing.py
    assert settings.DJPRESS_SETTINGS["CACHE_CATEGORIES"] is True

    category1 = Category.objects.create(title="Category 1", slug="category-1")
    category2 = Category.objects.create(title="Category 2", slug="category-2")

    category = Category.objects.get_category_by_slug("category-1")

    assert category == category1
    assert not category == category2


@pytest.mark.django_db
def test_get_category_by_slug_cache_disabled(settings):
    """Test that the get_category_by_slug method returns the correct category."""
    # Confirm the settings in settings_testing.py
    assert settings.DJPRESS_SETTINGS["CACHE_CATEGORIES"] is True

    settings.DJPRESS_SETTINGS["CACHE_CATEGORIES"] = False
    assert settings.DJPRESS_SETTINGS["CACHE_CATEGORIES"] is False

    category1 = Category.objects.create(title="Category 1", slug="category-1")
    category2 = Category.objects.create(title="Category 2", slug="category-2")

    category = Category.objects.get_category_by_slug("category-1")

    assert category == category1
    assert not category == category2


@pytest.mark.django_db
def test_get_category_by_slug_not_exists(settings):
    """Test that the get_category_by_slug method returns None when the category does not exist."""
    # Confirm the settings in settings_testing.py
    assert settings.DJPRESS_SETTINGS["CACHE_CATEGORIES"] is True

    settings.DJPRESS_SETTINGS["CACHE_CATEGORIES"] = False
    assert settings.DJPRESS_SETTINGS["CACHE_CATEGORIES"] is False

    with pytest.raises(ValueError) as excinfo:
        _ = Category.objects.get_category_by_slug("non-existent-category")
    assert "Category not found" in str(excinfo.value)


@pytest.mark.django_db
def test_category_permalink(settings):
    """Test that the permalink property returns the correct URL."""
    # Confirm the settings in settings_testing.py
    assert settings.DJPRESS_SETTINGS["CACHE_CATEGORIES"] is True
    assert settings.DJPRESS_SETTINGS["CATEGORY_ENABLED"] is True
    assert settings.DJPRESS_SETTINGS["CATEGORY_PREFIX"] == "test-url-category"

    category = Category.objects.create(title="Test Category", slug="test-category")

    assert category.permalink == "test-url-category/test-category"

    settings.DJPRESS_SETTINGS["CATEGORY_ENABLED"] = False
    settings.DJPRESS_SETTINGS["CATEGORY_PREFIX"] = ""

    assert category.permalink == "test-category"


@pytest.mark.django_db
def test_category_posts(test_post1, test_post2, category1, category2):
    assert list(category1.posts.all()) == [test_post1]
    assert list(category2.posts.all()) == [test_post2]

    test_post2.categories.set([category1])
    test_post2.save()
    assert list(category1.posts.all()) == [test_post1, test_post2]
    assert list(category2.posts.all()) == []


@pytest.mark.django_db
def test_category_has_posts(test_post1, test_post2, category1, category2):
    assert category1.has_posts is True
    assert category2.has_posts is True

    test_post2.categories.set([category1])
    test_post2.save()
    assert category1.has_posts is True
    assert category2.has_posts is False


@pytest.mark.django_db
def test_get_category_published(test_post1, test_post2, category1, category2):
    assert list(Category.objects.get_categories_with_published_posts()) == [category1, category2]

    test_post1.status = "draft"
    test_post1.save()
    assert list(Category.objects.get_categories_with_published_posts()) == [category2]

    test_post2.date = timezone.now() + timezone.timedelta(days=1)
    test_post2.save()
    assert list(Category.objects.get_categories_with_published_posts()) == []


@pytest.mark.django_db
def test_category_last_modified(test_post1, test_post2, category1, category2):
    assert category1.last_modified == test_post1.modified_date
    assert category2.last_modified == test_post2.modified_date

    test_post1.modified_date = timezone.now() + timezone.timedelta(days=1)
    test_post1.save()
    assert category1.last_modified == test_post1.modified_date

    test_post1.status = "draft"
    test_post1.save()
    assert category1.last_modified is None
