from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models.query_utils import DeferredAttribute

from utils import get_username_for_operation
from main.models import Product, Contractor, StorageItem, Operation
from .serializers import ProductSerializer, ContractorSerializer, StorageItemSerializer, OperationSerializer
from .pagination import CustomPagination
from .authentication import TokenAuthentication


class RegisteredViewSet(viewsets.ModelViewSet):

    def _get_model_field_values(self, element):
        result = []
        for key in sorted(self.model.__dict__.keys()):
            value = self.model.__dict__[key]
            if key != 'id' and isinstance(value, DeferredAttribute):
                result.append(getattr(element, key))
        return result

    def get_queryset(self):
        queryset = self.model.objects.all()
        order = self.request.query_params.get('order')
        if order:
            queryset = queryset.order_by(order)
        return queryset

    def register_create(self, request, *args, **kwargs):
        result = viewsets.ModelViewSet.create(self, request, *args, **kwargs)
        pk = result.data['id']
        created_element = self.model.objects.filter(pk=pk).first()
        if created_element:
            username = get_username_for_operation(request.user)
            operation = f'Создан {self.model_verbose_name}: {created_element}'
            Operation.objects.create(username=username, operation=operation)
        return result

    def register_update(self, request, *args, **kwargs):
        pk = kwargs['pk']
        updated_element = self.model.objects.filter(pk=pk).first()
        result = viewsets.ModelViewSet.update(self, request, *args, **kwargs)
        if updated_element:
            to_remove_before = updated_element.to_remove
            main_fields_before = self._get_model_field_values(updated_element)
            updated_element.refresh_from_db()
            to_remove_after = updated_element.to_remove
            main_fields_after = self._get_model_field_values(updated_element)

            username = get_username_for_operation(request.user)
            if main_fields_before != main_fields_after:
                operation = f'Изменен {self.model_verbose_name}: {updated_element}'
                Operation.objects.create(username=username, operation=operation)
            if not to_remove_before and to_remove_after:
                operation = f'{self.model_verbose_name} помечен на удаление: {updated_element}'
                Operation.objects.create(username=username, operation=operation)
            if to_remove_before and not to_remove_after:
                operation = f'Снята пометка на уделение с {self.model_verbose_name}: {updated_element}'
                Operation.objects.create(username=username, operation=operation)

        return result


class ProductViewSet(RegisteredViewSet):
    serializer_class = ProductSerializer
    pagination_class = CustomPagination
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['id', 'title', 'description']

    model = Product
    model_verbose_name = 'Товар'

    def create(self, request, *args, **kwargs):
        return RegisteredViewSet.register_create(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return RegisteredViewSet.register_update(self, request, *args, **kwargs)


class ContractorViewSet(RegisteredViewSet):
    serializer_class = ContractorSerializer
    pagination_class = CustomPagination
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['id', 'title']

    model = Contractor
    model_verbose_name = 'Контрагент'

    def create(self, request, *args, **kwargs):
        return RegisteredViewSet.register_create(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return RegisteredViewSet.register_update(self, request, *args, **kwargs)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def contractor_categories(request):
    data = {machine_name: human_name for machine_name, human_name in Contractor.CONTRACTOR_CATEGORY}
    return Response(data)


class OperationViesSet(viewsets.ModelViewSet):
    serializer_class = OperationSerializer
    pagination_class = CustomPagination
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['username', 'operation']
    queryset = Operation.objects.all()


class StorageItemViewSet(viewsets.ModelViewSet):
    serializer_class = StorageItemSerializer
    pagination_class = CustomPagination
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = StorageItem.objects.all()
