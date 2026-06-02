import pytest

from django import test
from django.core.cache import cache
from django.utils.text import slugify
from django.utils import timezone
from django.core.exceptions import ValidationError

from djpress.models.setting import Setting, SETTING_CACHE_KEY


@pytest.mark.django_db
def test_setting_save_uniqueness():
    """Test that an error is raised when trying to save a duplicate setting."""
    setting1 = Setting(key="SITE_TITLE", value="Test 1")
    setting1.save()

    setting2 = Setting(key="SITE_TITLE", value="Test 2")

    with pytest.raises(ValidationError) as excinfo:
        setting2.save()

    assert "Setting with this Key already exists." in str(excinfo.value)


@pytest.mark.django_db
def test_setting_str():
    """Test the str representation of the setting."""
    setting1 = Setting(key="SITE_TITLE", value="Test 1")
    setting1.save()

    assert str(setting1) == "SITE_TITLE: Test 1"
