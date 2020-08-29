from django.urls import path
from rest_framework import routers
from .views import index, ProductViewSet


urlpatterns = [
    path('', index, name='index')
]

router = routers.SimpleRouter()
router.register('api/products', ProductViewSet)
urlpatterns.extend(router.urls)
