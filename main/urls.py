from django.urls import path
from rest_framework import routers
from .views import index, ProductViewSet, products_to_xls

urlpatterns = [
    path('', index, name='index'),
    path('products_to_xls/', products_to_xls, name='products_to_xls')
]

router = routers.SimpleRouter()
router.register('api/products', ProductViewSet, basename='products')
urlpatterns.extend(router.urls)
