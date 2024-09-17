"""djpress admin configuration."""

from django.contrib import admin

# Register the models here.
from djpress.models import Category, Post

admin.site.register(Category)
admin.site.register(Post)
