"""Media file model for DJ Press."""

from pathlib import Path

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from djpress.conf import settings as djpress_settings


def upload_to_path(_instance: "Media", filename: str) -> str:
    """Generate the upload path for media files.

    Uses the configured MEDIA_UPLOAD_PATH setting to determine the upload location.
    Default path is 'djpress/YYYY/MM/DD/filename'.

    Args:
        filename: The original filename

    Returns:
        str: The path where the file should be uploaded
    """
    now = timezone.now()
    path_template = djpress_settings.MEDIA_UPLOAD_PATH

    # Remove spaces from the path - this lets us use {{year}} or {{ year }}
    path_template = path_template.replace(" ", "")

    # Replace date placeholders
    path = path_template.replace("{{year}}", now.strftime("%Y"))
    path = path.replace("{{month}}", now.strftime("%m"))
    path = path.replace("{{day}}", now.strftime("%d"))

    # Ensure path ends with a slash
    if not path.endswith("/"):
        path += "/"

    return f"{path}{filename}"


class MediaManager(models.Manager):
    """Manager for media files."""

    def get_by_type(self, media_type: str) -> models.QuerySet:
        """Get media files by type.

        Args:
            media_type: The media type to filter by

        Returns:
            QuerySet: A queryset of media files with the specified type
        """
        return self.filter(media_type=media_type)


class Media(models.Model):
    """Model for uploaded media files.

    This model stores information about uploaded media files like images,
    documents, audio, and video files.
    """

    MEDIA_TYPE_CHOICES = [
        ("image", "Image"),
        ("document", "Document"),
        ("audio", "Audio"),
        ("video", "Video"),
        ("other", "Other"),
    ]

    title = models.CharField("Title", max_length=255, help_text="A title for the media file")
    file = models.FileField("File", upload_to=upload_to_path, help_text="The uploaded file")
    media_type = models.CharField(
        "Media Type",
        max_length=20,
        choices=MEDIA_TYPE_CHOICES,
        default="image",
        help_text="The type of media file",
    )
    alt_text = models.CharField(
        "Alt Text",
        max_length=255,
        blank=True,
        help_text="Alternative text for images (for accessibility)",
    )
    description = models.TextField("Description", blank=True, help_text="A description of the media file")
    uploaded_by = models.ForeignKey(
        User,
        verbose_name="Uploaded By",
        on_delete=models.SET_NULL,
        null=True,
        related_name="media_files",
        help_text="The user who uploaded the file",
    )
    date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(auto_now=True)

    objects: MediaManager = MediaManager()

    class Meta:
        """Meta options for the Media model."""

        verbose_name = "Media"
        verbose_name_plural = "Media"
        ordering = ["-date"]

    def __str__(self) -> str:
        """Return a string representation of the media file.

        Returns:
            str: The title of the media file
        """
        return self.title

    @property
    def filename(self) -> str:
        """Get the original filename.

        Returns:
            str: The original filename
        """
        return Path(self.file.name).name

    @property
    def filesize(self) -> int:
        """Get the filesize in bytes.

        Returns:
            int: The filesize in bytes
        """
        return self.file.size

    @property
    def url(self) -> str:
        """Get the URL for the file.

        Returns:
            str: The URL for the file
        """
        return self.file.url

    @property
    def markdown_url(self) -> str:
        """Get the URL for the file in markdown format.

        Returns:
            str: The URL for the file in markdown format
        """
        if self.media_type == "image":
            return f'![{self.alt_text}]({self.url} "{self.title}")'

        return f"[{self.title}]({self.url})"
