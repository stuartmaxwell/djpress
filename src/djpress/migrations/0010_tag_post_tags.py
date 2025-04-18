# Generated by Django 5.1.4 on 2025-01-23 10:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("djpress", "0009_alter_post_options"),
    ]

    operations = [
        migrations.CreateModel(
            name="Tag",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=100, unique=True)),
                ("slug", models.SlugField(max_length=100, unique=True)),
            ],
            options={
                "verbose_name": "Tag",
                "verbose_name_plural": "Tags",
            },
        ),
        migrations.AddField(
            model_name="post",
            name="tags",
            field=models.ManyToManyField(blank=True, related_name="_posts", to="djpress.tag"),
        ),
    ]
