# Groups and Permissions

DJ Press offers four groups that can be used for managing content. These are in addition to the standard Django superuser role. And since content management is done through the Django Admin, all users need to be given `staff` status too.

There are four key permissions that are used to control access in DJ Press:

- Publish: there are two levels of publish permissions:
  - Can only publish own posts.
  - Can publish any posts.
- Create: can add a new post as a draft.
- Edit: there are two levels of edit permissions:
  - Can only edit own posts.
  - Can edit any posts.
- Delete: there are two levels of delete permissions:
  - Can only delete own posts.
  - Can delete any posts.

The four groups are:

- **djpress_admin**: Full permissions to all djpress models (posts, pages, categories, tags, media, plugin storage).
- **djpress_editor**: Full permissions over all content (posts, pages, categories, tags, media).
- **djpress_author**: Can publish, create, edit, and delete their own content. Unable to edit or delete other's posts.
- **djpress_contributor**: Can create, edit, and delete their own content. Unable to publish their own posts, nor edit or delete other's posts.

| Permission            | Admin | Editor | Author | Contributor |
| --------------------- | ----- | ------ | ------ | ----------- |
| Publish own posts     | ✅    | ✅     | ✅     | ✅          |
| Publish other's posts | ✅    | ✅     | ❌     | ❌          |
| Create draft posts    | ✅    | ✅     | ✅     | ✅          |
| Edit own posts        | ✅    | ✅     | ✅     | ✅          |
| Edit other's posts    | ✅    | ✅     | ❌     | ❌          |
| Delete own posts      | ✅    | ✅     | ✅     | ✅          |
| Delete other's posts  | ✅    | ✅     | ❌     | ❌          |
| Manage categories     | ✅    | ✅     | ❌     | ❌          |
| Manage tags           | ✅    | ✅     | ✅\*   | ✅\*        |
| Manage media          | ✅    | ✅     | ✅     | ✅          |
| Manage plugin storage | ✅    | ❌     | ❌     | ❌          |

\* Authors and Contributors can add tags but cannot edit or delete existing tags.

And of course, any account with superuser status can manage all models in your Django project.

## Group Setup

Groups are automatically created when you run `python manage.py migrate`. You can also manually create or update them by running:

```bash
python manage.py djpress_setup_groups
```

## Assigning Users to Groups

Groups are assigned by an account with superuser status, through the standard Django Admin interface, or via the Django shell:

```bash
python manage.py shell
>>> from django.contrib.auth.models import User, Group
>>> user = User.objects.get(username='your_username')
>>> user.groups.add(Group.objects.get(name='djpress_editor'))
```

## Group Name Prefix

All DJ Press groups are prefixed with `djpress_` to avoid conflicts with other groups you may have in your Django project.
