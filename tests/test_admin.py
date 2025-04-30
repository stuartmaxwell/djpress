"""Tests for the PostAdmin class."""

from django import test
from django.contrib.auth.models import Group
from django.test import RequestFactory
import pytest
from django.contrib.admin import site
from django.utils import timezone
from datetime import timedelta

from djpress.admin import PostAdmin
from djpress.models import Post
from djpress.url_utils import User
from tests.conftest import superuser
from djpress.admin import MediaAdmin
from djpress.models.media import Media


@pytest.fixture
def request_factory() -> RequestFactory:
    return RequestFactory()


@pytest.fixture
def post_admin():
    return PostAdmin(Post, site)


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


@pytest.mark.django_db
def test_queryset_superuser(
    test_post1: Post,
    test_post2: Post,
    test_post3: Post,
    request_factory: RequestFactory,
    superuser: User,
    post_admin: PostAdmin,
) -> None:
    """Test the get_queryset method for superusers."""

    # Create a request object
    request = request_factory.get("/")
    request.user = superuser

    # Test get_queryset method
    assert post_admin.get_queryset(request=request).count() == 3


@pytest.mark.django_db
def test_queryset_editor(
    test_post1: Post,
    test_post2: Post,
    test_post3: Post,
    user: User,
    post_admin: PostAdmin,
    request_factory: RequestFactory,
) -> None:
    """Test the get_queryset method for editors."""
    # Create an editor user
    editor_group = Group.objects.get(name="editor")
    user.groups.clear()  # Remove the user from all other groups
    user.groups.add(editor_group)

    # Create a request object
    request = request_factory.get("/")
    request.user = user

    qs = post_admin.get_queryset(request).count() == 3


@pytest.mark.django_db
def test_queryset_author(
    test_post1: Post,
    test_post2: Post,
    test_post3: Post,
    user: User,
    post_admin: PostAdmin,
    request_factory: RequestFactory,
) -> None:
    """Test the get_queryset method for authors.

    Authors should only see their own posts.
    """
    # Create an editor user
    author_group = Group.objects.get(name="author")
    user.groups.clear()  # Remove the user from all other groups
    user.groups.add(author_group)

    # Create a request object
    request = request_factory.get("/")
    request.user = user

    qs = post_admin.get_queryset(request).count() == 0

    test_post1.author = user
    test_post1.save()

    qs = post_admin.get_queryset(request).count() == 1

    test_post2.author = user
    test_post2.save()

    qs = post_admin.get_queryset(request).count() == 2


@pytest.mark.django_db
def test_queryset_contributor(
    test_post1: Post,
    test_post2: Post,
    test_post3: Post,
    user: User,
    post_admin: PostAdmin,
    request_factory: RequestFactory,
) -> None:
    """Test the get_queryset method for contributors.

    Contributors should only see their own posts.
    """
    # Create an editor user
    contributor_group = Group.objects.get(name="contributor")
    user.groups.clear()  # Remove the user from all other groups
    user.groups.add(contributor_group)

    # Create a request object
    request = request_factory.get("/")
    request.user = user

    qs = post_admin.get_queryset(request).count() == 0

    test_post1.author = user
    test_post1.save()

    qs = post_admin.get_queryset(request).count() == 1

    test_post2.author = user
    test_post2.save()

    qs = post_admin.get_queryset(request).count() == 2


@pytest.mark.django_db
def test_has_change_permission_superuser(
    superuser: User,
    post_admin: PostAdmin,
    request_factory: RequestFactory,
    test_post1: Post,
) -> None:
    request = request_factory.get("/")
    request.user = superuser

    assert post_admin.has_change_permission(request) is True  # General permission
    assert post_admin.has_change_permission(request, test_post1) is True  # Can edit any post


@pytest.mark.django_db
def test_has_change_permission_editor(
    user: User,
    post_admin: PostAdmin,
    request_factory: RequestFactory,
    test_post1: Post,
) -> None:
    """Test the has_change_permission method for editors.

    Editors can edit any post.
    """
    # Create an editor user that makes the request
    editor_user = User.objects.create_user(username="editor_user")
    editor_group = Group.objects.get(name="editor")
    editor_user.groups.clear()  # Remove the user from all other groups
    editor_user.groups.add(editor_group)
    request = request_factory.get("/")
    request.user = editor_user

    assert post_admin.has_change_permission(request) is True  # General permission
    assert post_admin.has_change_permission(request, test_post1) is True  # Can edit any post

    test_post1.author = editor_user
    test_post1.save()

    assert post_admin.has_change_permission(request, test_post1) is True  # Can edit own post


@pytest.mark.django_db
def test_has_change_permission_author(
    post_admin: PostAdmin,
    request_factory: RequestFactory,
    test_post1: Post,
) -> None:
    """Test the has_change_permission method for authors.

    Authors can only edit their own posts.
    """
    # Create an author user that makes the request
    author_user = User.objects.create_user(username="author_user")
    author_group = Group.objects.get(name="author")
    author_user.groups.clear()  # Remove the user from all other groups
    author_user.groups.add(author_group)
    request = request_factory.get("/")
    request.user = author_user

    assert post_admin.has_change_permission(request) is True  # General permission
    assert post_admin.has_change_permission(request, test_post1) is False  # Cannot edit any post

    test_post1.author = author_user
    test_post1.save()

    assert post_admin.has_change_permission(request, test_post1) is True  # Can edit own post


@pytest.mark.django_db
def test_has_change_permission_contributor(
    post_admin: PostAdmin,
    request_factory: RequestFactory,
    test_post1: Post,
) -> None:
    """Test the has_change_permission method for contributors.

    Authors can only edit their own posts.
    """
    # Create an contributor user that makes the request
    contributor_user = User.objects.create_user(username="contributor_user")
    contributor_group = Group.objects.get(name="contributor")
    contributor_user.groups.clear()  # Remove the user from all other groups
    contributor_user.groups.add(contributor_group)
    request = request_factory.get("/")
    request.user = contributor_user

    assert post_admin.has_change_permission(request) is True  # General permission
    assert post_admin.has_change_permission(request, test_post1) is False  # Cannot edit any post

    test_post1.author = contributor_user
    test_post1.save()

    assert post_admin.has_change_permission(request, test_post1) is True  # Can edit own post


@pytest.mark.django_db
def test_has_change_permission_regular_user(
    post_admin: PostAdmin,
    request_factory: RequestFactory,
    test_post1: Post,
) -> None:
    """Test the has_change_permission method for a regular user.

    A regular user that doesn't belong to any groups won't be able to edit.
    """
    # Create an regular user that makes the request
    regular_user = User.objects.create_user(username="regular_user")
    regular_user.groups.clear()  # Remove the user from all other groups
    request = request_factory.get("/")
    request.user = regular_user

    assert post_admin.has_change_permission(request) is False  # General permission
    assert post_admin.has_change_permission(request, test_post1) is False  # Cannot edit any post

    # Even if they are an author of a post, they can't edit it without permissions.
    test_post1.author = regular_user
    test_post1.save()

    assert post_admin.has_change_permission(request, test_post1) is False  # Can edit own post


@pytest.mark.django_db
def test_get_readonly_fields_superuser(superuser: User, post_admin: PostAdmin, request_factory: RequestFactory):
    request = request_factory.get("/")
    request.user = superuser

    readonly_fields = post_admin.get_readonly_fields(request)
    assert "status" not in readonly_fields  # Superuser can edit status


@pytest.mark.django_db
def test_get_readonly_fields_editor(user: User, post_admin: PostAdmin, request_factory: RequestFactory):
    editor_group = Group.objects.get(name="editor")
    user.groups.add(editor_group)
    request = request_factory.get("/")
    request.user = user

    readonly_fields = post_admin.get_readonly_fields(request)
    assert "status" not in readonly_fields  # Editor can edit status


@pytest.mark.django_db
def test_get_readonly_fields_author(user: User, post_admin: PostAdmin, request_factory: RequestFactory):
    author_group = Group.objects.get(name="author")
    user.groups.add(author_group)
    request = request_factory.get("/")
    request.user = user

    readonly_fields = post_admin.get_readonly_fields(request)
    assert "status" not in readonly_fields  # Author can edit status


@pytest.mark.django_db
def test_get_readonly_fields_contributor(user: User, post_admin: PostAdmin, request_factory: RequestFactory):
    contributor_group = Group.objects.get(name="contributor")
    user.groups.add(contributor_group)
    request = request_factory.get("/")
    request.user = user

    readonly_fields = post_admin.get_readonly_fields(request)
    assert "status" in readonly_fields  # Contributor cannot edit status


@pytest.mark.django_db
def test_post_admin_get_form(user):
    """Test the get_form method of the PostAdmin class."""

    # Create a request object
    request = RequestFactory().get("/")
    request.user = user

    # Create an instance of the PostAdmin class
    post_admin = PostAdmin(Post, site)

    # Get the form
    form = post_admin.get_form(request, None)

    # Check if the form is correct
    assert form is not None


@pytest.mark.django_db
def test_media_admin_get_form(user):
    """Test the get_form method of the MediaAdmin class."""

    # Create a request object
    request = RequestFactory().get("/")
    request.user = user

    # Create an instance of the MediaAdmin class
    media_admin = MediaAdmin(Media, site)

    # Get the form
    form = media_admin.get_form(request, None)

    # Check if the form is correct
    assert form is not None


@pytest.mark.django_db
def test_media_admin_preview(test_media_file_1, test_media_image_1):
    """Test the preview method of the MediaAdmin class."""

    # Create a request object
    request = RequestFactory().get("/")
    request.user = test_media_file_1.uploaded_by

    # Create an instance of the MediaAdmin class
    media_admin = MediaAdmin(Media, site)

    # Get the preview for a file
    preview_file = media_admin.preview(test_media_file_1)
    assert preview_file == "-"

    # Get the preview for an image
    preview_image = media_admin.preview(test_media_image_1)
    assert preview_image == f'<img src="{test_media_image_1.url}" style="max-height: 200px; max-width: 300px;">'


@pytest.mark.django_db
def test_media_admin_markdown_text(test_media_file_1, test_media_image_1):
    """Test the markdown_text method of the MediaAdmin class."""

    # Create a request object
    request = RequestFactory().get("/")
    request.user = test_media_file_1.uploaded_by

    # Create an instance of the MediaAdmin class
    media_admin = MediaAdmin(Media, site)

    # Get the markdown text for a file
    assert media_admin.markdown_text(test_media_file_1) == test_media_file_1.markdown_url

    # Get the markdown text for an image
    assert media_admin.markdown_text(test_media_image_1) == test_media_image_1.markdown_url
