# URL Structure

## Types of pages

- [Page](#page)
- [Post](#post)
- [Index](#index)

## Page

A page is a single piece of content stored in the `Post` table with a `post_type` of `page`. They are used to build static pages on your site that don't belong to categories, nor do they form part of any chronological structure, although they do have created and updated dates that can be used if desired. A page can have a parent (and that parent can have a parent), so that you can build a hierarchical menu. Typical examples are "About" pages or "Contact" pages.

## Post

A post is a single blog post stored in the `Post` table with a `post_type` of `post`. A post can belong to categories and tags, and have a created date that is used to display posts in a chronological order on an "Index" page. Posts also have an updated date field that can optionally be used if desired.

## Index

These are views that display a chronological list of blog posts that match a particular aspect. For example "/2024" would show all posts in the year 2024, or "/author/sam" shows all blog posts from the author called Sam. Index views have pagination to limit the number of posts displayed on a page which is configurable in the settings. Also, on an Index page, the posts are typically truncated to avoid polluting search engines with multiple copies of the same post on different URLs (although this is configurable).

### URL Types

- [Single post](#single-post) (Post)
- [Single page](#single-page) (Page)
- [Archive page](#archive-page) (Index)
- [Category page](#category-page) (Index)
- [Author page](#author-page) (Index)
- [Tag page](#tag-page) (Index)
- [Special URLs](#special-urls)

### Single post

URL structure - always ends with the post_slug:

- /{{ POST_PREFIX }}/{{ post_slug }}

Prefix is optional and configurable with the `POST_PREFIX` setting, and the default setting is `{{ year }}/{{ month }}/{{ day }}`. It's made up text and date fields, e.g.

- {{ year }}/{{ month }}/{{ day }} == "/2024/01/01/test-post"
- {{ year }}/{{ month }} == "/2024/01/test-post"
- {{ year }} == "/2024/test-post"
- post/{{ year }}/{{ month }}/{{ day }} == "/post/2024/01/01/test-post"
- {{ year }}/{{ month }}/{{ day }}/post == "/2024/01/01/post/test-post"
- foo{{ year }}bar{{ month }} == "/foo2024bar01/test-post"
- articles == "/articles/test-post"

### Single page

URL structure - can be either the slug name or with an optional parent:

- /{{ page_slug }}
- /{{ parent_page_slug }}/{{ page_slug }}

Note that the parent is a page itself, and this could also have a parent:

- /{{ parent_page_slug }}/{{ parent_page_slug }}/{{ page_slug }}
- /{{ parent_page_slug }}/{{ parent_page_slug }}/{{ parent_page_slug }}/{{ page_slug }}

### Archive page

URL structure - date-based URLs with an optional prefix:

- /{{ ARCHIVE_PREFIX }}/{{ year }}/{{ month }}/{{ day }}
- /{{ ARCHIVE_PREFIX }}/{{ year }}/{{ month }}
- /{{ ARCHIVE_PREFIX }}/{{ year }}

Prefix is an optional string, and is configurable with the `ARCHIVE_PREFIX` setting e.g.

- /2024/01/31
- /2024/01
- /2024/
- /archives/2024/01/31
- /archives/2024/01
- /archives/2024/

The `ARCHIVE_PREFIX` setting is configured as an empty string by default, so no prefix is used.

This feature is enabled by default, but can be disabled by setting `ARCHIVE_ENABLED` to `False`

### Category page

URL structure - a prefix and the category slug

- /{{ CATEGORY_PREFIX }}/{{ category_slug }}

The prefix is configurable with the `CATEGORY_PREFIX` setting, but is not optional, e.g.:

- /group/{{ category_slug }}
- /cat/{{ category_slug }}

However, browsing by category can be disabled with the `CATEGORY_ENABLED` setting. This is set to `True` by default.

### Author page

URL structure - a prefix and the author's username:

- /{{ AUTHOR_PREFIX }}/{{ author_username }}

The prefix is configurable with the `AUTHOR_PREFIX` setting, but is not optional:

- /writer/{{ author_username }}
- /a/{{ author_username }}

However, browsing by author can be disabled with the `AUTHOR_ENABLED` setting. This is set to `True` by default.

### Tag page

URL structure - a prefix and the tag slug.

- /{{ TAG_PREFIX }}/{{ tag_slug }}

Multiple tags can be combined so that only posts with all tags are displayed:

- /{{ TAG_PREFIX }}/{{ tag_slug }}+{{ tag_slug }}

The prefix is configurable with the `{{ TAG_PREFIX }}` setting, but is not optional:

- /topic/{{ tag_slug }}
- /t/{{ tag_slug }}

However, browsing by tag can be disabled with the `TAG_ENABLED` setting. This is set to `True` by default.

### Special URLs

There may be additional URL patterns that need to be resolved, that are not covered by the above rules.

#### RSS feed

- /{{ RSS_PATH }}

The `{{ RSS_PATH }}` setting is configurable but not optional. This is set to `rss` by default.

However, the RSS feed can be disabled with the `RSS_ENABLED` settings. This is set to `True` by default.

## URL Resolution

The order in which URLs are resolved is important since with non-unique slugs, and configurable prefixes, it's possible to create "overlapping" URLs. For example, consider the following URLs:

- A post with the URL: /2024/01/31/news
- A page with the URL: /news

Those two URLs are completely valid, but later the user could choose to remove the `POST_PREFIX` and then we would end up with the following two URLs:

- A post with the URL: /news
- A page with the URL: /news

To avoid excessive, and complex validation when modifying the settings, we will implement a URL resolution heirarchy which will determine which URL pattern matches first. Given the above example, we could choose to resolve posts first or to resolve pages first, which would determine which piece of content is displayed. This section will outline the order of priority.

1. Look for special URLs:
    1. RSS_PATH
2. Look for known prefixes:
    1. POST_PREFIX - this is a single post
    2. ARCHIVE_PREFIX - this is an archives index
    3. CATEGORY_PREFIX - this is a category index
    4. AUTHOR_PREFIX - this is an author index
    5. TAG_PREFIX - this is a tag index
3. If no valid prefix - this is a page

### Notes

1. POST_PREFIX
    - Translate the POST_PREFIX into a regex
    - Components used to make up the prefix (all optional):
        - Free form text, e.g. "post"
        - Year = {{ year }}  = `(?P<year>\d{4})`
        - Month = {{ month }} = `(?P<month>\d{2})`
        - Day = {{ day }} = `(?P<day>\d{2})`
    - e.g. "post/{{ year }}/{{ month }}/{{ day }}" = `r"/post/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})"`
    - The rest of the path is assumed to be the slug and used to find the post
        - If the POST_PREFIX has a date, use this to ensure the post matches the date
        - If multiple posts match, get the most recent post, e.g.
            - /post/2024/01/test-post - this could have been published on 2024/01/01
            - /post/2024/01/test-post - this could have been published on 2024/01/31
            - Both have the same URL, choose the most recent one.
2. ARCHIVE_PREFIX
    - First we need to calculate the "prefix" (effectively the full URL)
    - e.g. `r"/archives/(?P<year>\d{4})(?:/(?P<month>\d{2})(?:/(?P<day>\d{2}))?)?$"`
    - After matching, the year, month and day would need to be tested to ensure they are valid
    - If the date isn't valid, return an error (400?)
    - Then retrieve all posts matching that date

Unfinished notes...

1. CATEGORY_PREFIX
    - e.g. /category/...
    - The rest of the path is the category
    - If the category doesn't exist, return a 404
2. TAG_PREFIX
    - e.g. /tag/...
    - The rest of the path is the tag
    - If the tag doesn't exist, return a 404
3. AUTHOR_PREFIX
    - e.g. /author/...
    - The rest of the path is the author
    - If the author doesn't exist, return a 404
4. Other prefixes?
    - Media uploads?
    - What if we put the blog at the root of the site, and then created a page called "/static"? would that interfere with static files, or is that resolved earlier?
5. There is only one possible scenario left:
    - The URL is a page
    - We need to break up any URL parts to look for parents, e.g.
        - /company/news
        - /charities/news
        - /news
        - All three of those are different pages but with the same page-slug
