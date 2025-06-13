# Management Commands

DJ Press provides a Django management command to export your content to a flat-file Markdown format.

## djpress_export

The `djpress_export` command exports your DJ Press blog content to Markdown files in a format compatible with static site generators.

### Usage

```bash
python manage.py djpress_export [options]
```

### Options

- `--output-dir DIRECTORY`: Directory to export content to (default: `djpress_export`)
- `--posts-only`: Export only posts, not pages
- `--published-only`: Export only published content (excludes drafts and future posts)

### Examples

Export all content (posts and pages, including drafts):

```bash
python manage.py djpress_export
```

Export only published content to a custom directory:

```bash
python manage.py djpress_export --output-dir my_blog_export --published-only
```

Export only posts (no pages):

```bash
python manage.py djpress_export --posts-only
```

Export only published posts to a specific directory:

```bash
python manage.py djpress_export --output-dir blog_backup --posts-only --published-only
```

### Output Structure

The command creates the following directory structure:

```text
output_directory/
├── content/
│   ├── posts/
│   │   ├── 2024-01-15-my-first-post.md
│   │   └── 2024-02-20-another-post.md
│   └── pages/
│       ├── about.md
│       └── contact/
│           └── _index.md
```

### File Naming

- **Posts**: Named as `YYYY-MM-DD-slug.md` using the post's published date and slug
- **Pages**:
  - Top-level pages: `slug.md`
  - Nested pages: `parent-slug/child-slug/_index.md`

### Frontmatter

Each exported file includes YAML frontmatter with the following fields:

#### Common Fields (Posts and Pages)

- `title`: The post/page title
- `date`: Publication date in ISO format
- `lastmod`: Last modified date in ISO format
- `draft`: Boolean indicating if content is published
- `slug`: URL slug
- `author`: Author's full name or username

#### Post-Specific Fields

- `categories`: Array of category names (if any)
- `tags`: Array of tag names (if any)

#### Page-Specific Fields

- `type`: Always set to "page"
- `weight`: Menu order (if not 0)
- `parent`: Parent page slug (for nested pages)

### Example Output

**Post Example** (`2024-01-15-hello-world.md`):

```markdown
---
title: Hello World
date: 2024-01-15T10:30:00+00:00
lastmod: 2024-01-15T10:30:00+00:00
draft: false
slug: hello-world
author: John Doe
categories:
  - Technology
  - Django
tags:
  - blogging
  - web development
---

Welcome to my new blog! This is my first post using DJ Press.

## Getting Started

Here's how to get started with DJ Press...
```

**Page Example** (`about.md`):

```markdown
---
title: About Us
date: 2024-01-10T09:00:00+00:00
lastmod: 2024-01-10T09:00:00+00:00
draft: false
slug: about
author: Jane Smith
type: page
---

Learn more about our company and mission.
```

### Use Cases

#### Static Site Migration

Use this command when migrating from DJ Press to a static site generator:

```bash
python manage.py djpress_export --output-dir my_blog_export --published-only
```

#### Content Backup

Create a backup of all your content in a portable format:

```bash
python manage.py djpress_export --output-dir backup_$(date +%Y%m%d)
```

#### Draft Review

Export all content including drafts for review:

```bash
python manage.py djpress_export --output-dir review_content
```

### Static Site Generator Compatibility

The exported format is designed to work with popular static site generators:

#### Hugo

The default output structure matches Hugo's content organization. Files can be used directly in a Hugo site.

#### Jekyll

Files are compatible with Jekyll with minimal configuration changes. You may need to adjust the frontmatter format if using Jekyll-specific features.

#### Other Generators

Most static site generators that support Markdown with YAML frontmatter should work with the exported files.

### Notes

- The command preserves your original content structure and metadata
- Draft posts are exported with `draft: true` in the frontmatter
- Categories and tags are preserved as arrays in the frontmatter
- Parent/child page relationships are maintained through directory structure and frontmatter
- All dates are exported in ISO format for maximum compatibility
- File encoding is UTF-8 to support international content
