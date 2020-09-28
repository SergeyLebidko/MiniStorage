from django.urls import path
from .views import index, products, contractors, operations, storage_items, products_to_xls, contractors_to_xls

urlpatterns = [
    path('', index, name='index'),
    path('products/', products, name='products'),
    path('contractors/', contractors, name='contractors'),
    path('operations/', operations, name='operations'),
    path('products_to_xls/', products_to_xls, name='products_to_xls'),
    path('storage_items/', storage_items, name='storage_items'),
    path('contractors_to_xls/', contractors_to_xls, name='contractors_to_xls')
]
