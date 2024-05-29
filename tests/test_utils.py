import pytest
from djpress.utils import get_author_display_name
from django.contrib.auth.models import User


# create a parameterized fixture for a test user with first name, last name, and username
@pytest.fixture(
    params=[
        ("Sam", "Brown", "sambrown"),
        ("Sam", "", "sambrown"),
        ("", "Brown", "sambrown"),
        ("", "", "sambrown"),
    ]
)
def test_user(request):
    first_name, last_name, username = request.param
    user = User.objects.create_user(
        username=username,
        first_name=first_name,
        last_name=last_name,
        password="testpass",
    )

    return user


# Test the get_author_display_name function with the test_user fixture
@pytest.mark.django_db
def test_get_author_display_name(test_user):
    display_name = get_author_display_name(test_user)
    first_name = test_user.first_name
    last_name = test_user.last_name
    user_name = test_user.username

    # Assert that the display name is the first name and last name separated by a space
    if first_name and last_name:
        assert display_name == f"{first_name} {last_name}"

    if first_name and not last_name:
        assert display_name == first_name

    if not first_name and last_name:
        assert display_name == user_name

    if not first_name and not last_name:
        assert display_name == user_name
