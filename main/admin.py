from django.contrib import admin
from .models import Product, Contractor, Operation, StorageItem, Document, DocumentItem, Token


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


@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = ['username', 'operation', 'dt_created']


@admin.register(StorageItem)
class StorageItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'count', 'dt_created', 'dt_updated', 'to_remove']
    list_display_links = ['product']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['id', 'destination_type', 'apply_flag', 'contractor', 'dt_created', 'dt_updated', 'to_remove']
    list_display_links = ['destination_type', 'contractor']


@admin.register(DocumentItem)
class DocumentItemAdmin(admin.ModelAdmin):
    list_display = ['document', 'product', 'count']
    list_display_links = ['product']
