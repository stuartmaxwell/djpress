import pytest
from io import StringIO
from unittest.mock import patch

from django.contrib.auth.models import Group
from django.core.management import call_command
from django.core.management.base import CommandError

from djpress.management.commands.djpress_setup_groups import Command


@pytest.mark.django_db
class TestSetupGroups:
    """Test the djpress_setup_groups management command."""

    def test_command_help(self):
        """Test that the command help is displayed correctly."""
        command = Command()
        help_msg = (
            "Create or update DJ Press user groups (djpress_admin, djpress_editor, djpress_author, djpress_contributor), "
            "and assign appropriate permissions."
        )
        assert help_msg in command.help

    def test_command_creates_groups(self):
        """Test that the command successfully creates all groups."""
        # Delete groups if they exist (from migrations)
        Group.objects.filter(
            name__in=["djpress_admin", "djpress_editor", "djpress_author", "djpress_contributor"]
        ).delete()

        out = StringIO()
        call_command("djpress_setup_groups", stdout=out)

        # Check that all groups were created
        assert Group.objects.filter(name="djpress_admin").exists()
        assert Group.objects.filter(name="djpress_editor").exists()
        assert Group.objects.filter(name="djpress_author").exists()
        assert Group.objects.filter(name="djpress_contributor").exists()

        # Check output message
        output = out.getvalue()
        assert "Setting up DJ Press groups and permissions..." in output
        assert "Successfully created/updated DJ Press groups:" in output
        assert "djpress_admin" in output
        assert "djpress_editor" in output
        assert "djpress_author" in output
        assert "djpress_contributor" in output

    def test_command_updates_existing_groups(self):
        """Test that the command works when groups already exist."""
        # Groups should already exist from migrations, but create them if not
        Group.objects.get_or_create(name="djpress_admin")
        Group.objects.get_or_create(name="djpress_editor")
        Group.objects.get_or_create(name="djpress_author")
        Group.objects.get_or_create(name="djpress_contributor")

        out = StringIO()
        call_command("djpress_setup_groups", stdout=out)

        # Should still have exactly 4 groups (not duplicates)
        assert Group.objects.filter(name="djpress_admin").count() == 1
        assert Group.objects.filter(name="djpress_editor").count() == 1
        assert Group.objects.filter(name="djpress_author").count() == 1
        assert Group.objects.filter(name="djpress_contributor").count() == 1

        # Check success message
        output = out.getvalue()
        assert "Successfully created/updated DJ Press groups:" in output

    def test_command_handles_errors(self):
        """Test that the command handles errors gracefully."""
        with patch("djpress.management.commands.djpress_setup_groups.create_groups") as mock_create_groups:
            mock_create_groups.side_effect = Exception("Database error")

            with pytest.raises(CommandError) as exc_info:
                call_command("djpress_setup_groups")

            assert "Failed to set up groups: Database error" in str(exc_info.value)

    def test_command_output_styling(self):
        """Test that the command uses proper output styling."""
        out = StringIO()
        call_command("djpress_setup_groups", stdout=out)

        output = out.getvalue()
        # The SUCCESS style should be applied (though we can't test the actual styling,
        # we can verify the content is there)
        assert "Successfully created/updated DJ Press groups:" in output
        assert "Full permissions to all DJ Press models" in output
        assert "Can publish posts and manage all content" in output
        assert "Can publish their own posts and add tags/media" in output
        assert "Can create/edit posts (but not publish) and add tags/media" in output
