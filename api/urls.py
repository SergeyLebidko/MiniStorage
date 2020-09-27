from django.urls import path
from rest_framework import routers
from .views import ProductViewSet, ContractorViewSet, OperationViesSet, contractor_categories

urlpatterns = [
    path('contractor_categories/', contractor_categories, name='contractor_categories')
]

router = routers.SimpleRouter()
router.register('products', ProductViewSet, basename='products')
router.register('contractors', ContractorViewSet, basename='contractors')
router.register('operations', OperationViesSet)
urlpatterns.extend(router.urls)
