from django.urls import path
from .views import index, products, contractors, documents, operations, storage_items, products_to_xls, \
    contractors_to_xls, remove_marked_objects, import_products

app_name = 'main'

urlpatterns = [
    path('', index, name='index'),
    path('products/', products, name='products'),
    path('contractors/', contractors, name='contractors'),
    path('documents/', documents, name='documents'),
    path('operations/', operations, name='operations'),
    path('storage_items/', storage_items, name='storage_items'),
    path('products_to_xls/', products_to_xls, name='products_to_xls'),
    path('contractors_to_xls/', contractors_to_xls, name='contractors_to_xls'),
    path('remove_marked_objects/', remove_marked_objects, name='remove_marked_objects'),
    path('import_products/', import_products, name='import_products')
]
