"""Some extra tests for some bad logic that I fixed in the view dispatcher."""

import pytest
from django.urls import reverse
from djpress.models import Post, Category


@pytest.mark.django_db
def test_page_fallthrough_with_empty_post_prefix(client, settings, test_page1):
    """
    Test that a top-level page is reachable when POST_PREFIX is empty.

    If POST_PREFIX is empty, any top-level URL matches the Post regex.
    If no Post is found, it should fall through to the Page view.
    """
    settings.DJPRESS_SETTINGS["POST_PREFIX"] = ""

    # Ensure the page exists and has the slug we expect
    assert test_page1.post_type == "page"
    url = f"/{test_page1.slug}/"

    response = client.get(url)
    assert response.status_code == 200
    assert response.context["post"] == test_page1


@pytest.mark.django_db
def test_category_fallthrough_with_overlapping_prefix(client, settings, category1):
    """
    Test that a category is reachable if its URL matches the Post prefix pattern
    but no post exists.
    """
    # Setup: Post prefix is 'blog', Category prefix is also 'blog'
    settings.DJPRESS_SETTINGS["POST_PREFIX"] = "blog"
    settings.DJPRESS_SETTINGS["CATEGORY_PREFIX"] = "blog"

    # Path will be 'blog/category-slug'
    url = f"/blog/{category1.slug}/"

    # 1. Post regex: 'blog/(?P<slug>[\\w-]+)' matches 'blog/category-slug'
    # 2. get_post('category-slug') returns None
    # 3. Code should continue to Category check

    response = client.get(url)
    assert response.status_code == 200
    assert response.context["category"] == category1


@pytest.mark.django_db
def test_page_fallthrough_with_static_post_prefix(client, settings, user):
    """
    Test that a nested page under a path that matches POST_PREFIX is reachable.
    """
    settings.DJPRESS_SETTINGS["POST_PREFIX"] = "docs"

    # Create a page with slug 'setup'
    page = Post.admin_objects.create(
        title="Setup", slug="setup", content="Content", post_type="page", status="published", author=user
    )

    # URL is '/setup/'
    # Post regex 'docs/(?P<slug>[\\w-]+)' does NOT match '/setup/'
    # So this would work anyway.

    # What if the page IS under the prefix?
    # Create a page 'docs/intro'
    parent = Post.admin_objects.create(
        title="Docs", slug="docs", content="Content", post_type="page", status="published", author=user
    )
    child = Post.admin_objects.create(
        title="Intro", slug="intro", content="Content", post_type="page", status="published", author=user, parent=parent
    )

    url = "/docs/intro/"
    # Path is 'docs/intro'
    # Post regex 'docs/(?P<slug>[\\w-]+)' matches! slug='intro'
    # get_post('intro') will look for a POST with slug 'intro'.
    # It won't find one (it's a page).
    # Old code would 404 here.

    response = client.get(url)
    assert response.status_code == 200
    assert response.context["post"] == child
