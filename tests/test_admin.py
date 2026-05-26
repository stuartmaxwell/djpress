"""Tests for the PostAdmin class."""

from django import test
from django.contrib.auth.models import Group
from django.test import RequestFactory
import pytest
from django.contrib.admin import site
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from djpress.admin import PostAdmin, MediaAdmin, TagAdmin, CategoryAdmin
from djpress.models import Post, Media, Tag, Category
from tests.conftest import superuser
from djpress.admin import MediaAdmin
from djpress.models.media import Media
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.fixture
def request_factory() -> RequestFactory:
    return RequestFactory()


@pytest.fixture
def post_admin():
    return PostAdmin(Post, site)


@pytest.fixture
def media_admin():
    return MediaAdmin(Media, site)


@pytest.fixture
def tag_admin():
    return TagAdmin(Tag, site)


@pytest.fixture
def category_admin():
    return CategoryAdmin(Category, site)


@pytest.mark.django_db
def test_post_admin_published_status(test_post1):
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
    test_post1.published_at = timezone.now() + timedelta(days=1)
    test_post1.save()
    assert post_admin.published_status(test_post1) is False


@pytest.mark.django_db
def test_post_admin_formatted_date(test_post1):
    """Test the formatted_date method returns the correct date."""
    # Get the admin class
    post_admin = PostAdmin(Post, site)

    # Test formatted date
    assert post_admin.formatted_date(test_post1) == timezone.localtime(test_post1.published_at).strftime(
        "%Y-%m-%d %H:%M"
    )

    # Test future post
    test_post1.published_at = timezone.now() + timedelta(days=1)
    test_post1.save()

    assert (
        post_admin.formatted_date(test_post1)
        == f'<span style="color: #666;">{timezone.localtime(test_post1.published_at).strftime("%Y-%m-%d %H:%M")} (Scheduled)</span>'
    )


@pytest.mark.django_db
def test_post_admin_queryset_superuser(
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
def test_post_admin_queryset_admin(
    test_post1: Post,
    test_post2: Post,
    test_post3: Post,
    user: User,
    post_admin: PostAdmin,
    request_factory: RequestFactory,
) -> None:
    """Test the get_queryset method for admins."""
    # Create an admin user
    admin_group = Group.objects.get(name="djpress_admin")
    user.groups.clear()  # Remove the user from all other groups
    user.groups.add(admin_group)

    # Create a request object
    request = request_factory.get("/")
    request.user = user

    qs = post_admin.get_queryset(request).count() == 3


@pytest.mark.django_db
def test_post_admin_queryset_editor(
    test_post1: Post,
    test_post2: Post,
    test_post3: Post,
    user: User,
    post_admin: PostAdmin,
    request_factory: RequestFactory,
) -> None:
    """Test the get_queryset method for editors."""
    # Create an editor user
    editor_group = Group.objects.get(name="djpress_editor")
    user.groups.clear()  # Remove the user from all other groups
    user.groups.add(editor_group)

    # Create a request object
    request = request_factory.get("/")
    request.user = user

    qs = post_admin.get_queryset(request).count() == 3


@pytest.mark.django_db
def test_post_admin_queryset_author(
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
    author_group = Group.objects.get(name="djpress_author")
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
def test_post_admin_queryset_contributor(
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
    contributor_group = Group.objects.get(name="djpress_contributor")
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
def test_post_admin_has_change_permission_superuser(
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
def test_post_admin_has_change_permission_admin(
    user: User,
    post_admin: PostAdmin,
    request_factory: RequestFactory,
    test_post1: Post,
) -> None:
    """Test the has_change_permission method for admins.

    Admins can edit any post.
    """
    # Create an admin user that makes the request
    admin_user = User.objects.create_user(username="admin_user")
    admin_group = Group.objects.get(name="djpress_admin")
    admin_user.groups.clear()  # Remove the user from all other groups
    admin_user.groups.add(admin_group)
    request = request_factory.get("/")
    request.user = admin_user

    assert post_admin.has_change_permission(request) is True  # General permission
    assert post_admin.has_change_permission(request, test_post1) is True  # Can edit any post

    test_post1.author = admin_user
    test_post1.save()

    assert post_admin.has_change_permission(request, test_post1) is True  # Can edit own post


@pytest.mark.django_db
def test_post_admin_has_change_permission_editor(
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
    editor_group = Group.objects.get(name="djpress_editor")
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
def test_post_admin_has_change_permission_author(post_admin, request_factory, test_post1):
    """Test the has_change_permission method for authors.

    Authors can only edit their own posts.
    """
    # Create an author user that makes the request
    author_user = User.objects.create_user(username="author_user")
    author_group = Group.objects.get(name="djpress_author")
    author_user.groups.clear()  # Remove the user from all other groups
    author_user.groups.add(author_group)
    request = request_factory.get("/")
    request.user = author_user

    assert post_admin.has_change_permission(request) is False  # General permission
    assert post_admin.has_change_permission(request, test_post1) is False  # Cannot edit any post

    test_post1.author = author_user
    test_post1.save()

    assert post_admin.has_change_permission(request, test_post1) is True  # Can edit own post


@pytest.mark.django_db
def test_post_admin_has_change_permission_contributor(post_admin, request_factory, test_post1):
    """Test the has_change_permission method for contributors.

    Authors can only edit their own posts.
    """
    # Create an contributor user that makes the request
    contributor_user = User.objects.create_user(username="contributor_user")
    contributor_group = Group.objects.get(name="djpress_contributor")
    contributor_user.groups.clear()  # Remove the user from all other groups
    contributor_user.groups.add(contributor_group)
    request = request_factory.get("/")
    request.user = contributor_user

    assert post_admin.has_change_permission(request) is False  # General permission
    assert post_admin.has_change_permission(request, test_post1) is False  # Cannot edit any post

    test_post1.author = contributor_user
    test_post1.save()

    assert post_admin.has_change_permission(request, test_post1) is True  # Can edit own post


@pytest.mark.django_db
def test_post_admin_has_change_permission_regular_user(post_admin, request_factory, test_post1):
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
def test_post_admin_get_readonly_fields_superuser(
    superuser: User, post_admin: PostAdmin, request_factory: RequestFactory
):
    request = request_factory.get("/")
    request.user = superuser

    readonly_fields = post_admin.get_readonly_fields(request)
    assert readonly_fields == ["updated_at"]


@pytest.mark.django_db
def test_post_admin_get_readonly_fields_admin(user: User, post_admin: PostAdmin, request_factory: RequestFactory):
    admin_group = Group.objects.get(name="djpress_admin")
    user.groups.add(admin_group)
    request = request_factory.get("/")
    request.user = user

    readonly_fields = post_admin.get_readonly_fields(request)
    assert readonly_fields == ["updated_at"]


@pytest.mark.django_db
def test_post_admin_get_readonly_fields_editor(user: User, post_admin: PostAdmin, request_factory: RequestFactory):
    editor_group = Group.objects.get(name="djpress_editor")
    user.groups.add(editor_group)
    request = request_factory.get("/")
    request.user = user

    readonly_fields = post_admin.get_readonly_fields(request)
    assert readonly_fields == ["updated_at"]


@pytest.mark.django_db
def test_post_admin_get_readonly_fields_author(user: User, post_admin: PostAdmin, request_factory: RequestFactory):
    author_group = Group.objects.get(name="djpress_author")
    user.groups.add(author_group)
    request = request_factory.get("/")
    request.user = user

    readonly_fields = post_admin.get_readonly_fields(request)
    assert readonly_fields == ["updated_at", "author"]


@pytest.mark.django_db
def test_post_admin_get_readonly_fields_contributor(user: User, post_admin: PostAdmin, request_factory: RequestFactory):
    contributor_group = Group.objects.get(name="djpress_contributor")
    user.groups.add(contributor_group)
    request = request_factory.get("/")
    request.user = user

    readonly_fields = post_admin.get_readonly_fields(request)
    assert readonly_fields == ["updated_at", "author", "status"]


@pytest.mark.django_db
def test_media_admin_get_readonly_fields_superuser(superuser, media_admin, request_factory):
    request = request_factory.get("/")
    request.user = superuser

    readonly_fields = media_admin.get_readonly_fields(request)
    assert "updated_at" in readonly_fields


@pytest.mark.django_db
def test_media_admin_get_readonly_fields_admin(user, media_admin, request_factory):
    admin_group = Group.objects.get(name="djpress_admin")
    user.groups.add(admin_group)
    request = request_factory.get("/")
    request.user = user

    readonly_fields = media_admin.get_readonly_fields(request)
    assert "updated_at" in readonly_fields


@pytest.mark.django_db
def test_media_admin_get_readonly_fields_editor(user, media_admin, request_factory):
    editor_group = Group.objects.get(name="djpress_editor")
    user.groups.add(editor_group)
    request = request_factory.get("/")
    request.user = user

    readonly_fields = media_admin.get_readonly_fields(request)
    assert "updated_at" in readonly_fields


@pytest.mark.django_db
def test_media_admin_get_readonly_fields_author(user, media_admin, request_factory):
    author_group = Group.objects.get(name="djpress_author")
    user.groups.add(author_group)
    request = request_factory.get("/")
    request.user = user

    readonly_fields = media_admin.get_readonly_fields(request)
    assert "uploaded_by" in readonly_fields


@pytest.mark.django_db
def test_media_admin_get_readonly_fields_contributor(user, media_admin, request_factory):
    contributor_group = Group.objects.get(name="djpress_contributor")
    user.groups.add(contributor_group)
    request = request_factory.get("/")
    request.user = user

    readonly_fields = media_admin.get_readonly_fields(request)
    assert "uploaded_by" in readonly_fields


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


@pytest.mark.django_db
def test_media_admin_has_change_permission_superuser(superuser, media_admin, request_factory, test_media_file_1):
    request = request_factory.get("/")
    request.user = superuser

    assert media_admin.has_change_permission(request) is True  # General permission
    assert media_admin.has_change_permission(request, test_media_file_1) is True  # Can edit any file


@pytest.mark.django_db
def test_media_admin_has_change_permission_admin(user, media_admin, request_factory, test_media_file_1):
    """Test the has_change_permission method for admins.

    Admins can edit any media item.
    """
    # Create an admin user that makes the request
    admin_user = User.objects.create_user(username="admin_user")
    admin_group = Group.objects.get(name="djpress_admin")
    admin_user.groups.clear()  # Remove the user from all other groups
    admin_user.groups.add(admin_group)
    request = request_factory.get("/")
    request.user = admin_user

    assert media_admin.has_change_permission(request) is True  # General permission
    assert media_admin.has_change_permission(request, test_media_file_1) is True  # Can edit any file

    test_media_file_1.uploaded_by = admin_user
    test_media_file_1.save()

    assert media_admin.has_change_permission(request, test_media_file_1) is True  # Can edit own post


@pytest.mark.django_db
def test_media_admin_has_change_permission_editor(media_admin, request_factory, test_media_file_1):
    """Test the has_change_permission method for editors.

    Editors can edit any media item.
    """
    # Create an editor user that makes the request
    editor_user = User.objects.create_user(username="editor_user")
    editor_group = Group.objects.get(name="djpress_editor")
    editor_user.groups.clear()  # Remove the user from all other groups
    editor_user.groups.add(editor_group)
    request = request_factory.get("/")
    request.user = editor_user

    assert media_admin.has_change_permission(request) is True  # General permission
    assert media_admin.has_change_permission(request, test_media_file_1) is True  # Can edit any post

    test_media_file_1.uploaded_by = editor_user
    test_media_file_1.save()

    assert media_admin.has_change_permission(request, test_media_file_1) is True  # Can edit own post


@pytest.mark.django_db
def test_media_admin_has_change_permission_author(media_admin, request_factory, test_media_file_1):
    """Test the has_change_permission method for authors.

    Authors can only edit their own media items.
    """
    # Create an author user that makes the request
    author_user = User.objects.create_user(username="author_user")
    author_group = Group.objects.get(name="djpress_author")
    author_user.groups.clear()  # Remove the user from all other groups
    author_user.groups.add(author_group)
    request = request_factory.get("/")
    request.user = author_user

    assert media_admin.has_change_permission(request) is False  # General permission
    assert media_admin.has_change_permission(request, test_media_file_1) is False  # Cannot edit any file

    test_media_file_1.uploaded_by = author_user
    test_media_file_1.save()

    assert media_admin.has_change_permission(request, test_media_file_1) is True  # Can edit own file


@pytest.mark.django_db
def test_media_admin_has_change_permission_contributor(media_admin, request_factory, test_media_file_1):
    """Test the has_change_permission method for contributors.

    Contributors can only add new media
    """
    # Create an contributor user that makes the request
    contributor_user = User.objects.create_user(username="contributor_user")
    contributor_group = Group.objects.get(name="djpress_contributor")
    contributor_user.groups.clear()  # Remove the user from all other groups
    contributor_user.groups.add(contributor_group)
    request = request_factory.get("/")
    request.user = contributor_user

    assert media_admin.has_change_permission(request) is False  # General permission
    assert media_admin.has_change_permission(request, test_media_file_1) is False  # Cannot edit any file

    test_media_file_1.uploaded_by = contributor_user
    test_media_file_1.save()

    assert media_admin.has_change_permission(request, test_media_file_1) is False  # Cannot edit own file


@pytest.mark.django_db
def test_media_admin_has_change_permission_regular_user(media_admin, request_factory, test_media_file_1):
    """Test the has_change_permission method for a regular user.

    A regular user that doesn't belong to any groups won't be able to edit.
    """
    # Create an regular user that makes the request
    regular_user = User.objects.create_user(username="regular_user")
    regular_user.groups.clear()  # Remove the user from all other groups
    request = request_factory.get("/")
    request.user = regular_user

    assert media_admin.has_change_permission(request) is False  # General permission
    assert media_admin.has_change_permission(request, test_media_file_1) is False  # Cannot edit any post

    # Even if they are an uploaded_by of a media, they can't edit it without permissions.
    test_media_file_1.uploaded_by = regular_user
    test_media_file_1.save()

    assert media_admin.has_change_permission(request, test_media_file_1) is False  # Cannot edit any file


@pytest.mark.django_db
def test_media_admin_queryset_superuser(superuser, test_media_file_1, test_media_image_1, media_admin, request_factory):
    """Test the get_queryset method for superuser.

    Super users should see all media.
    """
    superuser.groups.clear()  # Remove the user from all groups

    # Create a request object
    request = request_factory.get("/")
    request.user = superuser

    assert media_admin.get_queryset(request).count() == 2


@pytest.mark.django_db
def test_media_admin_queryset_admin(test_media_file_1, test_media_image_1, media_admin, request_factory):
    """Test the get_queryset method for admins.

    Admins should see all media.
    """
    # Create a contributor user
    admin_user = User.objects.create_user(username="admin_user")
    admin_group = Group.objects.get(name="djpress_admin")
    admin_user.groups.clear()  # Remove the user from all other groups
    admin_user.groups.add(admin_group)

    # Create a request object
    request = request_factory.get("/")
    request.user = admin_user

    assert media_admin.get_queryset(request).count() == 2

    test_media_file_1.uploaded_by = admin_user
    test_media_file_1.save()

    assert media_admin.get_queryset(request).count() == 2

    test_media_image_1.uploaded_by = admin_user
    test_media_image_1.save()

    assert media_admin.get_queryset(request).count() == 2


@pytest.mark.django_db
def test_media_admin_queryset_editor(test_media_file_1, test_media_image_1, media_admin, request_factory):
    """Test the get_queryset method for editors.

    Editors should see all media.
    """
    # Create a contributor user
    editor_user = User.objects.create_user(username="editor_user")
    contributor_group = Group.objects.get(name="djpress_editor")
    editor_user.groups.clear()  # Remove the user from all other groups
    editor_user.groups.add(contributor_group)

    # Create a request object
    request = request_factory.get("/")
    request.user = editor_user

    assert media_admin.get_queryset(request).count() == 2

    test_media_file_1.uploaded_by = editor_user
    test_media_file_1.save()

    assert media_admin.get_queryset(request).count() == 2

    test_media_image_1.uploaded_by = editor_user
    test_media_image_1.save()

    assert media_admin.get_queryset(request).count() == 2


@pytest.mark.django_db
def test_media_admin_queryset_contributor(test_media_file_1, test_media_image_1, media_admin, request_factory):
    """Test the get_queryset method for contributors.

    Contributors should only see their own media.
    """
    # Create a contributor user
    contributor_user = User.objects.create_user(username="contributor_user")
    contributor_group = Group.objects.get(name="djpress_contributor")
    contributor_user.groups.clear()  # Remove the user from all other groups
    contributor_user.groups.add(contributor_group)

    # Create a request object
    request = request_factory.get("/")
    request.user = contributor_user

    assert media_admin.get_queryset(request).count() == 0

    test_media_file_1.uploaded_by = contributor_user
    test_media_file_1.save()

    assert media_admin.get_queryset(request).count() == 1

    test_media_image_1.uploaded_by = contributor_user
    test_media_image_1.save()

    assert media_admin.get_queryset(request).count() == 2


@pytest.mark.django_db
def test_media_admin_queryset_regular_user(test_media_file_1, test_media_image_1, media_admin, request_factory):
    """Test the get_queryset method for regular users.

    Regular users should only see their own media.
    """
    # Create a contributor user
    regular_user = User.objects.create_user(username="regular_user")
    regular_user.groups.clear()  # Remove the user from all other groups

    # Create a request object
    request = request_factory.get("/")
    request.user = regular_user

    assert media_admin.get_queryset(request).count() == 0

    test_media_file_1.uploaded_by = regular_user
    test_media_file_1.save()

    assert media_admin.get_queryset(request).count() == 1

    test_media_image_1.uploaded_by = regular_user
    test_media_image_1.save()

    assert media_admin.get_queryset(request).count() == 2


@pytest.mark.django_db
def test_post_admin_has_delete_permission_superuser(superuser, post_admin, request_factory, test_post1) -> None:
    """Test the has_delete_permission method for superusers."""
    superuser.groups.clear()

    request = request_factory.get("/")
    request.user = superuser

    assert post_admin.has_delete_permission(request) is True
    assert post_admin.has_delete_permission(request, test_post1) is True


@pytest.mark.django_db
def test_post_admin_has_delete_permission_admin(post_admin, request_factory, test_post1) -> None:
    """Test the has_delete_permission method for admins."""
    admin_user = User.objects.create_user(username="admin_user")
    admin_group = Group.objects.get(name="djpress_admin")
    admin_user.groups.clear()
    admin_user.groups.add(admin_group)

    request = request_factory.get("/")
    request.user = admin_user

    assert post_admin.has_delete_permission(request) is True
    assert post_admin.has_delete_permission(request, test_post1) is True

    test_post1.author = admin_user
    test_post1.save()

    assert post_admin.has_delete_permission(request, test_post1) is True


@pytest.mark.django_db
def test_post_admin_has_delete_permission_editor(post_admin, request_factory, test_post1) -> None:
    """Test the has_delete_permission method for editors."""
    editor_user = User.objects.create_user(username="editor_user")
    editor_group = Group.objects.get(name="djpress_editor")
    editor_user.groups.clear()
    editor_user.groups.add(editor_group)

    request = request_factory.get("/")
    request.user = editor_user

    assert post_admin.has_delete_permission(request) is True
    assert post_admin.has_delete_permission(request, test_post1) is True

    test_post1.author = editor_user
    test_post1.save()

    assert post_admin.has_delete_permission(request, test_post1) is True


@pytest.mark.django_db
def test_post_admin_has_delete_permission_author(post_admin, request_factory, test_post1) -> None:
    """Test the has_delete_permission method for authors/contributors."""
    author_user = User.objects.create_user(username="author_user")
    author_group = Group.objects.get(name="djpress_author")
    author_user.groups.clear()
    author_user.groups.add(author_group)

    request = request_factory.get("/")
    request.user = author_user

    assert post_admin.has_delete_permission(request) is False
    assert post_admin.has_delete_permission(request, test_post1) is False

    test_post1.author = author_user
    test_post1.save()

    assert post_admin.has_delete_permission(request, test_post1) is False


@pytest.mark.django_db
def test_post_admin_has_delete_permission_contributor(post_admin, request_factory, test_post1) -> None:
    """Test the has_delete_permission method for contributors."""
    contributor_user = User.objects.create_user(username="contributor_user")
    contributor = Group.objects.get(name="djpress_contributor")
    contributor_user.groups.clear()
    contributor_user.groups.add(contributor)

    request = request_factory.get("/")
    request.user = contributor_user

    assert post_admin.has_delete_permission(request) is False
    assert post_admin.has_delete_permission(request, test_post1) is False

    test_post1.author = contributor_user
    test_post1.save()

    assert post_admin.has_delete_permission(request, test_post1) is False


@pytest.mark.django_db
def test_media_admin_has_delete_permission_superuser(
    superuser, media_admin, request_factory, test_media_image_1
) -> None:
    """Test the has_delete_permission method for superusers."""
    superuser.groups.clear()

    request = request_factory.get("/")
    request.user = superuser

    assert media_admin.has_delete_permission(request) is True
    assert media_admin.has_delete_permission(request, test_media_image_1) is True


@pytest.mark.django_db
def test_media_admin_has_delete_permission_admin(media_admin, request_factory, test_media_image_1) -> None:
    """Test the has_delete_permission method for admins."""
    admin_user = User.objects.create_user(username="admin_user")
    admin_group = Group.objects.get(name="djpress_admin")
    admin_user.groups.clear()
    admin_user.groups.add(admin_group)

    request = request_factory.get("/")
    request.user = admin_user

    assert media_admin.has_delete_permission(request) is True
    assert media_admin.has_delete_permission(request, test_media_image_1) is True

    test_media_image_1.uploaded_by = admin_user
    test_media_image_1.save()

    assert media_admin.has_delete_permission(request, test_media_image_1) is True


@pytest.mark.django_db
def test_media_admin_has_delete_permission_editor(media_admin, request_factory, test_media_image_1) -> None:
    """Test the has_delete_permission method for editors."""
    editor_user = User.objects.create_user(username="editor_user")
    editor_group = Group.objects.get(name="djpress_editor")
    editor_user.groups.clear()
    editor_user.groups.add(editor_group)

    request = request_factory.get("/")
    request.user = editor_user

    assert media_admin.has_delete_permission(request) is True
    assert media_admin.has_delete_permission(request, test_media_image_1) is True

    test_media_image_1.uploaded_by = editor_user
    test_media_image_1.save()

    assert media_admin.has_delete_permission(request, test_media_image_1) is True


@pytest.mark.django_db
def test_media_admin_has_delete_permission_author(media_admin, request_factory, test_media_image_1) -> None:
    """Test the has_delete_permission method for authors/contributors."""
    author_user = User.objects.create_user(username="author_user")
    author_group = Group.objects.get(name="djpress_author")
    author_user.groups.clear()
    author_user.groups.add(author_group)

    request = request_factory.get("/")
    request.user = author_user

    assert media_admin.has_delete_permission(request) is False
    assert media_admin.has_delete_permission(request, test_media_image_1) is False

    test_media_image_1.uploaded_by = author_user
    test_media_image_1.save()

    assert media_admin.has_delete_permission(request, test_media_image_1) is False


@pytest.mark.django_db
def test_media_admin_has_delete_permission_contributor(media_admin, request_factory, test_media_image_1) -> None:
    """Test the has_delete_permission method for contributors."""
    contributor_user = User.objects.create_user(username="contributor_user")
    contributor = Group.objects.get(name="djpress_contributor")
    contributor_user.groups.clear()
    contributor_user.groups.add(contributor)

    request = request_factory.get("/")
    request.user = contributor_user

    assert media_admin.has_delete_permission(request) is False
    assert media_admin.has_delete_permission(request, test_media_image_1) is False

    test_media_image_1.uploaded_by = contributor_user
    test_media_image_1.save()

    assert media_admin.has_delete_permission(request, test_media_image_1) is False


@pytest.mark.django_db
def test_tag_admin_has_delete_permission_superuser(superuser, tag_admin, request_factory, tag1) -> None:
    """Test the has_delete_permission method for superusers."""
    superuser.groups.clear()

    request = request_factory.get("/")
    request.user = superuser

    assert tag_admin.has_delete_permission(request) is True
    assert tag_admin.has_delete_permission(request, tag1) is True


@pytest.mark.django_db
def test_tag_admin_has_delete_permission_admin(tag_admin, request_factory, tag1) -> None:
    """Test the has_delete_permission method for admins."""
    admin_user = User.objects.create_user(username="admin_user")
    admin_group = Group.objects.get(name="djpress_admin")
    admin_user.groups.clear()
    admin_user.groups.add(admin_group)

    request = request_factory.get("/")
    request.user = admin_user

    assert tag_admin.has_delete_permission(request) is True
    assert tag_admin.has_delete_permission(request, tag1) is True


@pytest.mark.django_db
def test_tag_admin_has_delete_permission_editor(tag_admin, request_factory, tag1) -> None:
    """Test the has_delete_permission method for editors."""
    editor_user = User.objects.create_user(username="editor_user")
    editor_group = Group.objects.get(name="djpress_editor")
    editor_user.groups.clear()
    editor_user.groups.add(editor_group)

    request = request_factory.get("/")
    request.user = editor_user

    assert tag_admin.has_delete_permission(request) is True
    assert tag_admin.has_delete_permission(request, tag1) is True


@pytest.mark.django_db
def test_tag_admin_has_delete_permission_author(tag_admin, request_factory, tag1) -> None:
    """Test the has_delete_permission method for authors/contributors."""
    author_user = User.objects.create_user(username="author_user")
    author_group = Group.objects.get(name="djpress_author")
    author_user.groups.clear()
    author_user.groups.add(author_group)

    request = request_factory.get("/")
    request.user = author_user

    assert tag_admin.has_delete_permission(request) is False
    assert tag_admin.has_delete_permission(request, tag1) is False


@pytest.mark.django_db
def test_tag_admin_has_delete_permission_contributor(tag_admin, request_factory, tag1) -> None:
    """Test the has_delete_permission method for contributors."""
    contributor_user = User.objects.create_user(username="contributor_user")
    contributor = Group.objects.get(name="djpress_contributor")
    contributor_user.groups.clear()
    contributor_user.groups.add(contributor)

    request = request_factory.get("/")
    request.user = contributor_user

    assert tag_admin.has_delete_permission(request) is False
    assert tag_admin.has_delete_permission(request, tag1) is False


@pytest.mark.django_db
def test_tag_admin_has_change_permission_superuser(superuser, tag_admin, request_factory, tag1) -> None:
    """Test the has_change_permission method for superusers."""
    superuser.groups.clear()

    request = request_factory.get("/")
    request.user = superuser

    assert tag_admin.has_change_permission(request) is True
    assert tag_admin.has_change_permission(request, tag1) is True


@pytest.mark.django_db
def test_tag_admin_has_change_permission_admin(tag_admin, request_factory, tag1) -> None:
    """Test the has_change_permission method for admins."""
    admin_user = User.objects.create_user(username="admin_user")
    admin_group = Group.objects.get(name="djpress_admin")
    admin_user.groups.clear()
    admin_user.groups.add(admin_group)

    request = request_factory.get("/")
    request.user = admin_user

    assert tag_admin.has_change_permission(request) is True
    assert tag_admin.has_change_permission(request, tag1) is True


@pytest.mark.django_db
def test_tag_admin_has_change_permission_editor(tag_admin, request_factory, tag1) -> None:
    """Test the has_change_permission method for editors."""
    editor_user = User.objects.create_user(username="editor_user")
    editor_group = Group.objects.get(name="djpress_editor")
    editor_user.groups.clear()
    editor_user.groups.add(editor_group)

    request = request_factory.get("/")
    request.user = editor_user

    assert tag_admin.has_change_permission(request) is True
    assert tag_admin.has_change_permission(request, tag1) is True


@pytest.mark.django_db
def test_tag_admin_has_change_permission_author(tag_admin, request_factory, tag1) -> None:
    """Test the has_change_permission method for authors/contributors."""
    author_user = User.objects.create_user(username="author_user")
    author_group = Group.objects.get(name="djpress_author")
    author_user.groups.clear()
    author_user.groups.add(author_group)

    request = request_factory.get("/")
    request.user = author_user

    assert tag_admin.has_change_permission(request) is False
    assert tag_admin.has_change_permission(request, tag1) is False


@pytest.mark.django_db
def test_tag_admin_has_change_permission_contributor(tag_admin, request_factory, tag1) -> None:
    """Test the has_change_permission method for contributors."""
    contributor_user = User.objects.create_user(username="contributor_user")
    contributor = Group.objects.get(name="djpress_contributor")
    contributor_user.groups.clear()
    contributor_user.groups.add(contributor)

    request = request_factory.get("/")
    request.user = contributor_user

    assert tag_admin.has_change_permission(request) is False
    assert tag_admin.has_change_permission(request, tag1) is False


@pytest.mark.django_db
def test_category_admin_has_delete_permission_superuser(superuser, category_admin, request_factory, category1) -> None:
    """Test the has_delete_permission method for superusers."""
    superuser.groups.clear()

    request = request_factory.get("/")
    request.user = superuser

    assert category_admin.has_delete_permission(request) is True
    assert category_admin.has_delete_permission(request, category1) is True


@pytest.mark.django_db
def test_category_admin_has_delete_permission_admin(category_admin, request_factory, category1) -> None:
    """Test the has_delete_permission method for admins."""
    admin_user = User.objects.create_user(username="admin_user")
    admin_group = Group.objects.get(name="djpress_admin")
    admin_user.groups.clear()
    admin_user.groups.add(admin_group)

    request = request_factory.get("/")
    request.user = admin_user

    assert category_admin.has_delete_permission(request) is True
    assert category_admin.has_delete_permission(request, category1) is True


@pytest.mark.django_db
def test_category_admin_has_delete_permission_editor(category_admin, request_factory, category1) -> None:
    """Test the has_delete_permission method for editors."""
    editor_user = User.objects.create_user(username="editor_user")
    editor_group = Group.objects.get(name="djpress_editor")
    editor_user.groups.clear()
    editor_user.groups.add(editor_group)

    request = request_factory.get("/")
    request.user = editor_user

    assert category_admin.has_delete_permission(request) is True
    assert category_admin.has_delete_permission(request, category1) is True


@pytest.mark.django_db
def test_category_admin_has_delete_permission_author(category_admin, request_factory, category1) -> None:
    """Test the has_delete_permission method for authors/contributors."""
    author_user = User.objects.create_user(username="author_user")
    author_group = Group.objects.get(name="djpress_author")
    author_user.groups.clear()
    author_user.groups.add(author_group)

    request = request_factory.get("/")
    request.user = author_user

    assert category_admin.has_delete_permission(request) is False
    assert category_admin.has_delete_permission(request, category1) is False


@pytest.mark.django_db
def test_category_admin_has_delete_permission_contributor(category_admin, request_factory, category1) -> None:
    """Test the has_delete_permission method for contributors."""
    contributor_user = User.objects.create_user(username="contributor_user")
    contributor = Group.objects.get(name="djpress_contributor")
    contributor_user.groups.clear()
    contributor_user.groups.add(contributor)

    request = request_factory.get("/")
    request.user = contributor_user

    assert category_admin.has_delete_permission(request) is False
    assert category_admin.has_delete_permission(request, category1) is False


@pytest.mark.django_db
def test_category_admin_has_change_permission_superuser(superuser, category_admin, request_factory, category1) -> None:
    """Test the has_change_permission method for superusers."""
    superuser.groups.clear()

    request = request_factory.get("/")
    request.user = superuser

    assert category_admin.has_change_permission(request) is True
    assert category_admin.has_change_permission(request, category1) is True


@pytest.mark.django_db
def test_category_admin_has_change_permission_admin(category_admin, request_factory, category1) -> None:
    """Test the has_change_permission method for admins."""
    admin_user = User.objects.create_user(username="admin_user")
    admin_group = Group.objects.get(name="djpress_admin")
    admin_user.groups.clear()
    admin_user.groups.add(admin_group)

    request = request_factory.get("/")
    request.user = admin_user

    assert category_admin.has_change_permission(request) is True
    assert category_admin.has_change_permission(request, category1) is True


@pytest.mark.django_db
def test_category_admin_has_change_permission_editor(category_admin, request_factory, category1) -> None:
    """Test the has_change_permission method for editors."""
    editor_user = User.objects.create_user(username="editor_user")
    editor_group = Group.objects.get(name="djpress_editor")
    editor_user.groups.clear()
    editor_user.groups.add(editor_group)

    request = request_factory.get("/")
    request.user = editor_user

    assert category_admin.has_change_permission(request) is True
    assert category_admin.has_change_permission(request, category1) is True


@pytest.mark.django_db
def test_category_admin_has_change_permission_author(category_admin, request_factory, category1) -> None:
    """Test the has_change_permission method for authors/contributors."""
    author_user = User.objects.create_user(username="author_user")
    author_group = Group.objects.get(name="djpress_author")
    author_user.groups.clear()
    author_user.groups.add(author_group)

    request = request_factory.get("/")
    request.user = author_user

    assert category_admin.has_change_permission(request) is False
    assert category_admin.has_change_permission(request, category1) is False


@pytest.mark.django_db
def test_category_admin_has_change_permission_contributor(category_admin, request_factory, category1) -> None:
    """Test the has_change_permission method for contributors."""
    contributor_user = User.objects.create_user(username="contributor_user")
    contributor = Group.objects.get(name="djpress_contributor")
    contributor_user.groups.clear()
    contributor_user.groups.add(contributor)

    request = request_factory.get("/")
    request.user = contributor_user

    assert category_admin.has_change_permission(request) is False
    assert category_admin.has_change_permission(request, category1) is False


@pytest.mark.django_db
def test_post_admin_save_model(request_factory, user, post_admin):
    """Test the save_model method for the PostAdmin.

    Author should be set automatically when creating a new Post.
    """
    request = request_factory.get("/")
    request.user = user

    new_post = Post(title="test_no_author_1", content="Test 1")
    post_admin.save_model(request, obj=new_post, form=None, change=False)

    saved_post = Post.admin_objects.get(title="test_no_author_1")
    assert saved_post.author == user


@pytest.mark.django_db
def test_media_admin_save_model(request_factory, user, media_admin):
    """Test the save_model method for the MediaAdmin.

    Uploaded By should be set automatically when creating a new Media.
    """
    request = request_factory.get("/")
    request.user = user

    dummy_file = SimpleUploadedFile("dummy.jpg", b"file_content", content_type="image/jpeg")
    new_media = Media(title="Media 1", file=dummy_file, media_type="image")

    media_admin.save_model(request, obj=new_media, form=None, change=False)

    saved_media = Media.objects.get(title="Media 1")
    assert saved_media.uploaded_by == user
    # Clean up the file from the filesystem after creation
    if saved_media.file:
        saved_media.file.delete(save=False)
