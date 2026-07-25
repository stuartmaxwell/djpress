import pytest

from djpress.sitemaps import DateBasedSitemap, PostSitemap, PageSitemap, CategorySitemap
from djpress.url_utils import get_archives_url, get_category_url
from djpress.models import Post


@pytest.mark.django_db
def test_post_sitemap(test_post1, test_post2, test_post3):
    """Test the PostSitemap class."""

    expected_items = [test_post1, test_post2, test_post3]

    sitemap = PostSitemap()

    assert sitemap.changefreq == "monthly"
    assert sitemap.protocol == "https"
    assert len(sitemap.items()) == len(expected_items)
    assert sitemap.lastmod(test_post1) == test_post1.updated_at
    assert sitemap.location(test_post1) == test_post1.url
    assert sitemap.lastmod(test_post2) == test_post2.updated_at
    assert sitemap.location(test_post2) == test_post2.url
    assert sitemap.lastmod(test_post3) == test_post3.updated_at
    assert sitemap.location(test_post3) == test_post3.url


@pytest.mark.django_db
def test_page_sitemap(test_page1, test_page2, test_page3):
    """Test the PageSitemap class."""

    expected_items = [test_page1, test_page2, test_page3]

    sitemap = PageSitemap()

    assert sitemap.changefreq == "monthly"
    assert sitemap.protocol == "https"
    assert len(sitemap.items()) == len(expected_items)
    assert sitemap.lastmod(test_page1) == test_page1.updated_at
    assert sitemap.location(test_page1) == test_page1.url
    assert sitemap.lastmod(test_page2) == test_page2.updated_at
    assert sitemap.location(test_page2) == test_page2.url
    assert sitemap.lastmod(test_page3) == test_page3.updated_at
    assert sitemap.location(test_page3) == test_page3.url


@pytest.mark.django_db
def test_category_sitemap(category1, category2, test_post1, test_post2):
    """Test the CategorySitemap class."""

    expected_items = [category1, category2]

    sitemap = CategorySitemap()

    assert sitemap.changefreq == "daily"
    assert sitemap.protocol == "https"
    assert len(sitemap.items()) == len(expected_items)
    assert sitemap.lastmod(category1) == test_post1.updated_at
    assert sitemap.lastmod(category2) == test_post2.updated_at
    assert sitemap.location(category1) == get_category_url(category1)


@pytest.mark.django_db
def test_date_based_sitemap(test_post1, test_post2, test_post3):
    """Test the DateBasedSitemap class."""

    # DateBasedSitemap groups by `_date`, the frozen local publish date - not `published_at`,
    # which is stored in UTC - so the expected values must come from `_date` too.
    expected_items = [
        {"year": test_post3._date.year, "latest_modified": test_post3.updated_at},
        {
            "year": test_post3._date.year,
            "month": test_post3._date.month,
            "latest_modified": test_post3.updated_at,
        },
        {
            "year": test_post3._date.year,
            "month": test_post3._date.month,
            "day": test_post3._date.day,
            "latest_modified": test_post3.updated_at,
        },
    ]

    sitemap = DateBasedSitemap()

    assert sitemap.changefreq == "daily"
    assert sitemap.protocol == "https"
    assert sitemap.items() == expected_items
    assert sitemap.lastmod(expected_items[0]) == test_post3.updated_at
    assert sitemap.location(expected_items[0]) == get_archives_url(test_post3._date.year)
    assert sitemap.location(expected_items[1]) == get_archives_url(test_post3._date.year, test_post3._date.month)
    assert sitemap.location(expected_items[2]) == get_archives_url(
        test_post3._date.year, test_post3._date.month, test_post3._date.day
    )


@pytest.mark.django_db
def test_date_based_sitemap_archives_disabled(settings, test_post1, test_post2, test_post3):
    # Check that we have three published posts
    assert Post.post_objects.count() == 3

    # Disable the archives
    settings.DJPRESS_SETTINGS["ARCHIVE_ENABLED"] = False

    # Create a new sitemap
    sitemap = DateBasedSitemap()

    # Check that the items are empty
    assert sitemap.items() == []
