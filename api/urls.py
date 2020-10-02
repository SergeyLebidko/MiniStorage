from django.urls import path
from rest_framework import routers
from .views import ProductViewSet, ContractorViewSet, OperationViesSet, StorageItemViewSet, DocumentViewSet, \
    contractor_categories, document_destinations

urlpatterns = [
    path('contractor_categories/', contractor_categories, name='contractor_categories'),
    path('document_destinations/', document_destinations, name='document_destinations')
]

router = routers.SimpleRouter()
router.register('products', ProductViewSet, basename='products')
router.register('contractors', ContractorViewSet, basename='contractors')
router.register('operations', OperationViesSet)
router.register('documents', DocumentViewSet, basename='documents')
router.register('storage_items', StorageItemViewSet, basename='storage_items')
urlpatterns.extend(router.urls)
