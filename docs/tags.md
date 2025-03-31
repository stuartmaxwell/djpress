# Tags

Tags can be added to your blog posts to help index and organise them. Tags are similar to categories in that they can be used to categorise your posts, but tags are meant to be more flexible and non-heirachical and used to label and index your posts.

## Settings

The following three settings can be used to configure the tags feature:

- [TAG_ENABLED](#tag_enabled): boolean, default is True.
- [TAG_PREFIX](#tag_prefix): string, default is "tag".
- [CACHE_TAGS](#cache_tags): boolean, default is False.

### TAG_ENABLED

This setting enables or disables the tag feature from being visible to visitors, the default setting is True. Note that the Tag model will still exist, and you are still able to add tags to your posts, but no tags will be viewable or accessible to visitors - this is useful if you want to use tags to organise your blog posts, but don't need or want them visible.

### TAG_PREFIX

This configures the URL prefix that is used for the tag feature, the default is "tag" - i.e. `https://yourblog.com/tag/example-tag`. This setting must be set to a non-empty string value for the tag feature to be enabled. For example, even with `TAG_ENABLED=True`, if you set `TAG_PREFIX=""`, the tag feature will be disabled.

### CACHE_TAGS

Enabling this setting will cache tags, using the cache settings that have been configured in your Django project. While this can improve performance, caching is an advanced topic and should be handled carefully. There are signals configured to invalidate the tag caceh when new tags or posts are created.
