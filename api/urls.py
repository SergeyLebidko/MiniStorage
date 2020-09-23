from rest_framework import routers
from .views import ProductViewSet, ContractorViewSet

urlpatterns = []

router = routers.SimpleRouter()
router.register('products', ProductViewSet, basename='products')
router.register('contractors', ContractorViewSet, basename='contractors')
urlpatterns.extend(router.urls)
