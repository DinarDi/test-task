from django.contrib import admin

from product.models import Product, ProductAccess


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'title', 'start_date', 'price']


@admin.register(ProductAccess)
class ProductAccessAdmin(admin.ModelAdmin):
    pass
