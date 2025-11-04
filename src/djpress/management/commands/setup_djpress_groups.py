"""Management command to set up DJ Press groups and permissions."""

from django.core.management.base import BaseCommand, CommandError

from djpress.permissions import create_groups


class Command(BaseCommand):
    """Set up DJ Press groups and permissions."""

    help = (
        "Create or update DJ Press user groups (djpress_admin, djpress_editor, djpress_author, djpress_contributor), "
        "and assign appropriate permissions."
    )

    def handle(self, **options) -> None:  # noqa: ANN003, ARG002
        """Handle the setup command."""
        self.stdout.write("Setting up DJ Press groups and permissions...")

        try:
            create_groups()

            self.stdout.write(
                self.style.SUCCESS(
                    "Successfully created/updated DJ Press groups:\n"
                    "  - djpress_admin: Full permissions to all DJ Press models\n"
                    "  - djpress_editor: Can publish posts and manage all content\n"
                    "  - djpress_author: Can publish their own posts and add tags/media\n"
                    "  - djpress_contributor: Can create/edit posts (but not publish) and add tags/media",
                ),
            )
        except Exception as e:
            msg = f"Failed to set up groups: {e}"
            raise CommandError(msg) from e
