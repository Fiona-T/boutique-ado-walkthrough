from django.contrib import admin
from .models import Product, Category


class ProductAdmin(admin.ModelAdmin):
    """admin site settings for Product model"""
    list_display = (
        'sku',
        'name',
        'category',
        'price',
        'rating',
        'image',
    )

    ordering = ('sku',)


class CategoryAdmin(admin.ModelAdmin):
    """admin site settings for Category model"""
    list_display = (
        'friendly_name',
        'name',
    )


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
