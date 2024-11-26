"""Tests for the PostAdmin class."""

import pytest
from django.contrib.admin import site
from django.utils import timezone
from datetime import timedelta

from djpress.admin import PostAdmin
from djpress.models import Post


@pytest.mark.django_db
def test_published_status(test_post1):
    """Test the published_status method returns correct boolean values."""
    # Get the admin class
    post_admin = PostAdmin(Post, site)

    # Test published post
    assert post_admin.published_status(test_post1) is True

    # Chnage to draft
    test_post1.status = "draft"
    test_post1.save()
    assert post_admin.published_status(test_post1) is False

    # Change to future post
    test_post1.status = "published"
    test_post1.date = timezone.now() + timedelta(days=1)
    test_post1.save()
    assert post_admin.published_status(test_post1) is False


@pytest.mark.django_db
def test_formatted_date(test_post1):
    """Test the formatted_date method returns the correct date."""
    # Get the admin class
    post_admin = PostAdmin(Post, site)

    # Test formatted date
    assert post_admin.formatted_date(test_post1) == test_post1.date.strftime("%Y-%m-%d %H:%M")

    # Test future post
    test_post1.date = timezone.now() + timedelta(days=1)
    test_post1.save()

    assert (
        post_admin.formatted_date(test_post1)
        == f'<span style="color: #666;">{test_post1.date.strftime("%Y-%m-%d %H:%M")} (Scheduled)</span>'
    )
