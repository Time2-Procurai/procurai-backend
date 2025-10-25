from django.contrib import admin
from .models import Product, Category

# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'owner',
        'price',
        'is_negotiable',
        'category',
        'is_service',
        'available',
        'created_at',
        'updated_at'
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
