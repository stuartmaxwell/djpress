import pytest

from djpress.models import PluginStorage


@pytest.mark.django_db
def test_plugin_storage_model():
    test_plugin = PluginStorage.objects.create(plugin_name="test_plugin")

    assert str(test_plugin) == "test_plugin"


@pytest.mark.django_db
def test_plugin_storage_get_data():
    """Test getting plugin data."""
    # Test empty case (no storage exists)
    data = PluginStorage.objects.get_data("test_plugin")
    assert data == {}

    # Test with stored data
    PluginStorage.objects.save_data("test_plugin", {"key": "value"})
    data = PluginStorage.objects.get_data("test_plugin")
    assert data == {"key": "value"}


@pytest.mark.django_db
def test_plugin_storage_save_data():
    """Test saving plugin data."""
    # Test creating new storage
    PluginStorage.objects.save_data("test_plugin", {"key": "value"})
    storage = PluginStorage.objects.get(plugin_name="test_plugin")
    assert storage.plugin_data == {"key": "value"}

    # Test updating existing storage
    PluginStorage.objects.save_data("test_plugin", {"new_key": "new_value"})
    storage.refresh_from_db()
    assert storage.plugin_data == {"new_key": "new_value"}
