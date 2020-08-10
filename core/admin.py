from django.contrib import admin

from django.apps import apps
from .models import *

# Register your models here.
models = apps.get_models()


class CategoryInline(admin.TabularInline):
    model = Category.products.through


class ProductAdmin(admin.ModelAdmin):
    """Product admin."""
    model = Product
    inlines = [
        CategoryInline,
    ]


for model in models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
