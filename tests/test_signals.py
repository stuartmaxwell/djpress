from django.contrib.contenttypes.models import ContentType
import pytest

from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission

from djpress.models import Post


@pytest.fixture
def post_content_type() -> ContentType:
    return ContentType.objects.get_for_model(Post)


@pytest.mark.django_db
def test_groups_created() -> None:
    # This should run post_migrate signal
    from django.core.management import call_command

    call_command("migrate")

    # Check groups exist
    assert Group.objects.filter(name="editor").exists()
    assert Group.objects.filter(name="author").exists()
    assert Group.objects.filter(name="contributor").exists()


@pytest.mark.django_db
def test_group_permissions(post_content_type: ContentType) -> None:
    editor = Group.objects.get(name="editor")
    author = Group.objects.get(name="author")
    contributor = Group.objects.get(name="contributor")

    # Check publish permission
    publish_perm = Permission.objects.get(content_type=post_content_type, codename="can_publish_post")
    assert publish_perm in editor.permissions.all()
    assert publish_perm in author.permissions.all()
    assert publish_perm not in contributor.permissions.all()


@pytest.mark.django_db
def test_grou_category_permissions(post_content_type: ContentType) -> None:
    editor = Group.objects.get(name="editor")
    author = Group.objects.get(name="author")
    contributor = Group.objects.get(name="contributor")

    # Check category permissions
    category_perms = Permission.objects.filter(
        content_type=post_content_type, codename__in=["add_category", "change_category", "delete_category"]
    )
    for perm in category_perms:
        assert perm in editor.permissions.all()
        assert perm not in author.permissions.all()
        assert perm not in contributor.permissions.all()
