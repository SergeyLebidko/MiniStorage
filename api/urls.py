from django.urls import path
from rest_framework import routers
from .views import ProductViewSet, ContractorViewSet, OperationViesSet, StorageItemViewSet, DocumentViewSet, \
    DocumentItemViewSet, contractor_categories, apply_document, unapply_document, remove_marked_objects, \
    import_products, consolidated_report, motion_report

app_name = 'api'

urlpatterns = [
    path('contractor_categories/', contractor_categories, name='contractor_categories'),
    path('apply_document/<int:document_id>/', apply_document, name='apply_document'),
    path('unapply_document/<int:document_id>/', unapply_document, name='unapply_document'),
    path('remove_marked_objects/', remove_marked_objects, name='remove_marked_objects'),
    path('import_products/', import_products, name='import_products'),
    path('consolidated_report/', consolidated_report, name='consolidated_report'),
    path('motion_report/', motion_report, name='motion_report')
]

router = routers.SimpleRouter()
router.register('products', ProductViewSet, basename='products')
router.register('contractors', ContractorViewSet, basename='contractors')
router.register('operations', OperationViesSet)
router.register('documents', DocumentViewSet, basename='documents')
router.register('document_items', DocumentItemViewSet, basename='document_items')
router.register('storage_items', StorageItemViewSet, basename='storage_items')
urlpatterns.extend(router.urls)
