from django.contrib.contenttypes.models import ContentType
import pytest

from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission


@pytest.mark.django_db
def test_groups_created() -> None:
    # This should run post_migrate signal
    from django.core.management import call_command

    call_command("migrate")

    # Check groups exist
    assert Group.objects.filter(name="djpress_admin").exists()
    assert Group.objects.filter(name="djpress_editor").exists()
    assert Group.objects.filter(name="djpress_author").exists()
    assert Group.objects.filter(name="djpress_contributor").exists()
