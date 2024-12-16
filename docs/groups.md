# Groups and Permissions

DJ Press offers three groups that can be used for managing content. These are in addition to the standard Django superuser role. And since content management is done through the Django Admin, all users need to be given `staff` status too.

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

The three groups are:

- Editor: have full permissions over all content.
- Author: can publish, create, edit, and delete their own content. Unable to edit or delete other's posts.
- Contributor: can create, edit, and delete their own content. Unable to publish their own posts, nor edit or delete other's posts.

| Permission | Editor | Author | Contributor |
|------------|--------|--------|-------------|
| Publish own posts | ✅ | ✅ | ❌ |
| Publish other's posts | ✅ | ❌ | ❌ |
| Create draft posts | ✅ | ✅ | ✅ |
| Edit own posts | ✅ | ✅ | ✅ |
| Edit other's posts | ✅ | ❌ | ❌ |
| Delete own posts | ✅ | ✅ | ✅ |
| Delete other's posts | ✅ | ❌ | ❌ |

In addition to managing the post contents, Editors can also manage categories.

And of course, any account with superuser status can manage all models in your Django project.

Groups are assigned by an account with superuser status, through the standard Django Admin interface.
