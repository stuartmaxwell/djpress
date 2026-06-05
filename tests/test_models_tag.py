import pytest

from django import test
from django.core.cache import cache
from django.utils.text import slugify
from django.utils import timezone

from djpress.models.tag import Tag, TAG_CACHE_KEY


@pytest.mark.django_db
def test_tag_model(tag1):
    tag = Tag.objects.create(title="Test Tag", slug="test-tag")
    assert tag.title == "Test Tag"
    assert tag.slug == "test-tag"
    assert str(tag) == "Test Tag"


@pytest.mark.django_db
def test_tag_save_slug_generation():
    """Test that the slug is correctly generated when saving a Tag."""
    tag = Tag(title="Test Tag")
    tag.save()

    assert tag.slug == slugify("Test Tag")


@pytest.mark.django_db
def test_tag_save_slug_uniqueness():
    """Test that an error is raised when trying to save a Tag with a duplicate slug."""
    tag1 = Tag(title="Test Tag")
    tag1.save()

    tag2 = Tag(title="Test Tag")

    with pytest.raises(ValueError) as excinfo:
        tag2.save()

    assert str(excinfo.value) == f"A tag with the slug {tag2.slug} already exists."


@pytest.mark.django_db
def test_tag_save_invalid_name():
    """Test that an error is raised when trying to save a Tag with an invalid name."""
    tag = Tag(title="-")

    with pytest.raises(ValueError) as excinfo:
        tag.save()

    assert str(excinfo.value) == "Invalid title. Unable to generate a valid slug."


@pytest.mark.django_db
def test_tag_slug_auto_generation():
    # Test case 1: Slug auto-generated when not provided
    tag1 = Tag.objects.create(title="Test Tag")
    assert tag1.slug == slugify(tag1.title)

    # Test case 2: Slug not overridden when provided
    tag2 = Tag.objects.create(title="Another Tag", slug="custom-slug")
    assert tag2.slug == "custom-slug"

    # Test case 3: Slug auto-generated with special characters
    tag3 = Tag.objects.create(title="Special !@#$%^&*() Tag")
    assert tag3.slug == "special-tag"

    # Test case 4: Slug auto-generated with non-ASCII characters
    tag4 = Tag.objects.create(title="Non-ASCII áéíóú Tag")
    assert tag4.slug == "non-ascii-aeiou-tag"

    # Test case 5: Slug auto-generated with leading/trailing hyphens
    tag5 = Tag.objects.create(title="--Leading/Trailing Hyphens--")
    assert tag5.slug == "leadingtrailing-hyphens"

    # Test case 6: Raise ValueError for invalid title
    with pytest.raises(ValueError) as exc_info:
        Tag.objects.create(title="!@#$%^&*()")
    assert str(exc_info.value) == "Invalid title. Unable to generate a valid slug."


@pytest.mark.django_db
def test_get_tags_cache_enabled(settings, tag1, tag2, tag3):
    """Test that the get_tags method returns the correct tags."""
    # Confirm the settings in settings_testing.py
    settings.DJPRESS_SETTINGS["CACHE_TAGS"] = True
    assert settings.DJPRESS_SETTINGS["CACHE_TAGS"] is True

    tags = Tag.objects.get_tags()

    assert list(tags) == [tag1, tag2, tag3]


@pytest.mark.django_db
def test_get_tags_cache_disabled(settings, tag1, tag2, tag3):
    """Test that the get_tags method returns the correct tags."""
    # Confirm the settings in settings_testing.py
    settings.DJPRESS_SETTINGS["CACHE_TAGS"] = False
    assert settings.DJPRESS_SETTINGS["CACHE_TAGS"] is False

    tags = Tag.objects.get_tags()

    assert list(tags) == [tag1, tag2, tag3]


@pytest.mark.django_db
def test_get_cached_tags(settings, tag1, tag2, tag3):
    """Test that the _get_cached_tags method returns the correct tags."""
    # Confirm the settings in settings_testing.py
    settings.DJPRESS_SETTINGS["CACHE_TAGS"] = False
    assert settings.DJPRESS_SETTINGS["CACHE_TAGS"] is False

    tags = Tag.objects.get_tags()
    cache.set(TAG_CACHE_KEY, tags)

    settings.DJPRESS_SETTINGS["CACHE_TAGS"] = True
    assert settings.DJPRESS_SETTINGS["CACHE_TAGS"] is True

    tags = Tag.objects._get_cached_tags()
    assert list(tags) == [tag1, tag2, tag3]

    # Now the queryset should be cached
    cached_queryset = cache.get(TAG_CACHE_KEY)
    assert list(tags) == list(cached_queryset)


@pytest.mark.django_db
def test_get_tag_by_slug_cache_enabled(settings, tag1, tag2):
    """Test that the get_tag_by_slug method returns the correct tag."""
    # Confirm the settings in settings_testing.py
    settings.DJPRESS_SETTINGS["CACHE_TAGS"] = True
    assert settings.DJPRESS_SETTINGS["CACHE_TAGS"] is True

    tag = Tag.objects.get_tag_by_slug(tag1.slug)

    assert tag == tag1
    assert not tag == tag2

    with pytest.raises(ValueError) as excinfo:
        tag = Tag.objects.get_tag_by_slug("non-existent-tag")


@pytest.mark.django_db
def test_get_category_by_slug_cache_disabled(settings, tag1, tag2):
    """Test that the get_tag_by_slug method returns the correct category."""
    # Confirm the settings in settings_testing.py
    settings.DJPRESS_SETTINGS["CACHE_TAGS"] = False
    assert settings.DJPRESS_SETTINGS["CACHE_TAGS"] is False

    tag = Tag.objects.get_tag_by_slug(tag1.slug)

    assert tag == tag1
    assert not tag == tag2

    with pytest.raises(ValueError) as excinfo:
        tag = Tag.objects.get_tag_by_slug("non-existent-tag")


@pytest.mark.django_db
def test_get_tag_by_slug_not_exists(settings):
    """Test that the get_tag_by_slug method returns None when the tag does not exist."""
    # Confirm the settings in settings_testing.py
    settings.DJPRESS_SETTINGS["CACHE_TAGS"] = False
    assert settings.DJPRESS_SETTINGS["CACHE_TAGS"] is False

    with pytest.raises(ValueError) as excinfo:
        _ = Tag.objects.get_tag_by_slug("non-existent-tag")
    assert "Tag not found" in str(excinfo.value)


@pytest.mark.django_db
def test_tag_url(settings):
    """Test that the url property returns the correct URL."""
    # Confirm the settings in settings_testing.py
    assert settings.DJPRESS_SETTINGS["TAG_ENABLED"] is True
    assert settings.DJPRESS_SETTINGS["TAG_PREFIX"] == "test-url-tag"

    tag = Tag.objects.create(title="Test Tag", slug="test-tag")

    assert tag.url == "/test-url-tag/test-tag/"

    settings.DJPRESS_SETTINGS["TAG_ENABLED"] = False
    settings.DJPRESS_SETTINGS["TAG_PREFIX"] = ""

    assert tag.url == "/"


@pytest.mark.django_db
def test_tag_posts(test_post1, test_post2, tag1, tag2):
    test_post1.tags.add(tag1)
    test_post2.tags.add(tag2)
    assert list(tag1.posts.all()) == [test_post1]
    assert list(tag2.posts.all()) == [test_post2]

    test_post2.tags.add(tag1)
    assert list(tag1.posts.all()) == [test_post2, test_post1]
    assert list(tag2.posts.all()) == [test_post2]


@pytest.mark.django_db
def test_tag_has_posts(test_post1, test_post2, tag1, tag2):
    assert tag1.has_posts is False
    assert tag2.has_posts is False

    test_post1.tags.add(tag1)
    assert tag1.has_posts is True
    assert tag2.has_posts is False

    test_post2.tags.add(tag2)
    assert tag1.has_posts is True
    assert tag2.has_posts is True

    test_post1.status = "draft"
    test_post1.save()
    assert tag1.has_posts is False
    assert tag2.has_posts is True

    test_post2.published_at = timezone.now() + timezone.timedelta(days=1)
    test_post2.save()
    assert tag1.has_posts is False
    assert tag2.has_posts is False


@pytest.mark.django_db
def test_get_tags_with_counts(test_post1, test_post2, tag1, tag2, tag3):
    # Initially no tags have published posts
    tags = list(Tag.objects.get_tags_with_counts(published_only=True))
    assert tags == []

    # If published_only=False, all tags should be returned with num_posts=0
    all_tags = list(Tag.objects.get_tags_with_counts(published_only=False).order_by("title"))
    assert len(all_tags) == 3
    assert {t.title for t in all_tags} == {tag1.title, tag2.title, tag3.title}
    for tag in all_tags:
        assert tag.num_posts == 0

    # Associate posts with tags
    test_post1.tags.add(tag1)
    test_post2.tags.add(tag2)

    # Now get_tags_with_counts(published_only=True) should return tag1 and tag2, sorted or not, let's sort them
    published_tags = list(Tag.objects.get_tags_with_counts(published_only=True).order_by("title"))
    assert len(published_tags) == 2
    # Check that the annotated count is 1 for each
    tag1_with_count = next(t for t in published_tags if t.pk == tag1.pk)
    tag2_with_count = next(t for t in published_tags if t.pk == tag2.pk)
    assert tag1_with_count.num_posts == 1
    assert tag2_with_count.num_posts == 1

    # When test_post1 becomes a draft, it shouldn't be counted, and tag1 shouldn't be returned when published_only=True
    test_post1.status = "draft"
    test_post1.save()
    published_tags = list(Tag.objects.get_tags_with_counts(published_only=True))
    assert len(published_tags) == 1
    assert published_tags[0].pk == tag2.pk
    assert published_tags[0].num_posts == 1

    # If published_only=False, tag1 is still returned but with count 0
    all_tags = list(Tag.objects.get_tags_with_counts(published_only=False).order_by("title"))
    assert len(all_tags) == 3
    tag1_with_count = next(t for t in all_tags if t.pk == tag1.pk)
    tag2_with_count = next(t for t in all_tags if t.pk == tag2.pk)
    assert tag1_with_count.num_posts == 0
    assert tag2_with_count.num_posts == 1

    # When test_post2 published_at is set to future, tag2 shouldn't be returned when published_only=True
    test_post2.published_at = timezone.now() + timezone.timedelta(days=1)
    test_post2.save()
    published_tags = list(Tag.objects.get_tags_with_counts(published_only=True))
    assert published_tags == []


@pytest.mark.django_db
def test_tag_last_modified(test_post1, test_post2, tag1, tag2):
    test_post1.tags.add(tag1)
    test_post2.tags.add(tag2)

    assert tag1.last_modified == test_post1.updated_at
    assert tag2.last_modified == test_post2.updated_at

    test_post1.updated_at = timezone.now() + timezone.timedelta(days=1)
    test_post1.save()
    assert tag1.last_modified == test_post1.updated_at

    test_post1.status = "draft"
    test_post1.save()
    assert tag1.last_modified is None
