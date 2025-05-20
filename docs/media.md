# Media Management

DJ Press uses the built-in Django media management system that allows you to upload, manage, and use various types of media files in your content.

## Overview

The Media management feature provides:

- File uploads with automatic date-based organisation
- Custom upload paths, configurable through the settings
- Support for different media types (images, documents, audio, video, etc.)
- Admin interface for managing uploaded files
- Easy insertion of media into content using markdown syntax
- Support for image alt text and descriptions for accessibility

## Media Model

The Media model is designed to store information about uploaded files and handle various media types.

### Media Types

DJ Press supports the following media types:

- `image`: Image files (jpg, png, gif, etc.)
- `document`: Document files (pdf, doc, txt, etc.)
- `audio`: Audio files (mp3, wav, etc.)
- `video`: Video files (mp4, mov, etc.)
- `other`: Other file types

### Key Fields

- `title`: A descriptive title for the media file
- `file`: The actual uploaded file
- `media_type`: The type of media (image, document, audio, video, other)
- `alt_text`: Alternative text for images (for accessibility)
- `description`: A description of the media file
- `uploaded_by`: The user who uploaded the file
- `date`: The upload date and time
- `modified_date`: The last modification date and time

## Configuration

### Media Upload Path

You can configure the upload path for media files using the `MEDIA_UPLOAD_PATH` setting:

```python
DJPRESS_SETTINGS = {
    # ... other settings ...
    "MEDIA_UPLOAD_PATH": "djpress/{{ year }}/{{ month }}/{{ day }}",
}
```

This setting supports the following variables:

- `{{ year }}`: The current year (e.g., 2025)
- `{{ month }}`: The current month (e.g., 04)
- `{{ day }}`: The current day (e.g., 29)

The default path is `djpress/{{ year }}/{{ month }}/{{ day }}`, which creates a directory structure like `djpress/2025/04/29/`.

## Using Media in Content

### Markdown Syntax

Once you've uploaded media files, you can use them in your content using markdown syntax:

#### Images

```markdown
![Alt text](/media/path/to/image.jpg "Optional title")
```

#### Other Media

```markdown
[File Title](/media/path/to/file.pdf)
```

### Getting Markdown URLs

For convenience, the Media model provides a `markdown_url` property that generates the correct markdown syntax for the file, which you can copy directly from the admin interface:

- **Images**: `![alt_text](/media/path/to/image.jpg "title")`
- **Other files**: `[title](/media/path/to/file.pdf)`

## Admin Interface

The Media admin interface provides a user-friendly way to manage your media files:

### Features

- List view showing all media files with filters for type, date, and uploader
- Search functionality for finding files by title, description, or alt text
- Preview thumbnail for image files
- Automatic capture of metadata (file size, dates)
- Ready-to-use markdown syntax for easy embedding in content

### Permissions

Media uploads and management follow Django's permissions system:

- Superusers and staff with appropriate permissions can upload and manage all media
- The user who uploads a file is automatically set as the `uploaded_by` field

## Best Practices

1. **Use Alt Text**: Always provide descriptive alt text for images to improve accessibility
2. **Organise With Titles**: Use clear, descriptive titles to make files easy to find
3. **Optimise Images**: Optimise large images before uploading to improve page load times
4. **Use Appropriate Types**: Select the correct media type when uploading files
5. **Consider File Size**: Be mindful of file sizes, especially for images and videos
