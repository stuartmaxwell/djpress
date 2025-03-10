# Generated by Django 5.1.3 on 2024-12-16 04:08

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("djpress", "0008_alter_post_options_alter_post_managers_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="post",
            options={
                "default_manager_name": "admin_objects",
                "permissions": [("can_publish_post", "Can publish post")],
                "verbose_name": "post",
                "verbose_name_plural": "posts",
            },
        ),
    ]
