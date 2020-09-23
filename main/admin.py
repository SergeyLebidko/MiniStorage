from django.contrib import admin
from .models import Product, Contractor, Token


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ['token', 'user']
    list_display_links = ['token', 'user']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'description', 'price', 'dt_created', 'dt_updated', 'to_remove']
    list_display_links = ['title', 'description', 'price']


@admin.register(Contractor)
class ContractorAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category', 'dt_created', 'dt_updated', 'to_remove']
    list_display_links = ['title']
