from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models.query_utils import DeferredAttribute

from utils import get_username_for_operation
from main.models import Product, Contractor, StorageItem, Document, DocumentItem, Operation
from .serializers import ProductSerializer, ContractorSerializer, StorageItemSerializer, OperationSerializer, \
    DocumentSerializer, DocumentItemSerializer
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

    def create(self, request, *args, **kwargs):
        result = viewsets.ModelViewSet.create(self, request, *args, **kwargs)
        pk = result.data['id']
        created_element = self.model.objects.filter(pk=pk).first()
        if created_element:
            username = get_username_for_operation(request.user)
            operation = f'Создан {self.model_verbose_name}: {created_element}'
            Operation.objects.create(username=username, operation=operation)
        return result

    def update(self, request, *args, **kwargs):
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


class ContractorViewSet(RegisteredViewSet):
    serializer_class = ContractorSerializer
    pagination_class = CustomPagination
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['id', 'title']

    model = Contractor
    model_verbose_name = 'Контрагент'


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def contractor_categories(request):
    return Response(dict(Contractor.CONTRACTOR_CATEGORY))


class OperationViesSet(viewsets.ModelViewSet):
    serializer_class = OperationSerializer
    pagination_class = CustomPagination
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['username', 'operation']
    queryset = Operation.objects.all()


class StorageItemViewSet(RegisteredViewSet):
    serializer_class = StorageItemSerializer
    pagination_class = CustomPagination
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['product__id', 'product__title']

    model = StorageItem
    model_verbose_name = 'Товар на складе'

    def get_queryset(self):
        queryset = StorageItem.objects.all()
        order = self.request.query_params.get('order')
        if order:
            if order.endswith('product_title'):
                prefix = '-' if order.startswith('-') else ''
                queryset = queryset.order_by(f'{prefix}product__title')
            else:
                queryset = queryset.order_by(order)
        return queryset


class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    pagination_class = CustomPagination
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Document.objects.all()

        # Обрабатываем параметры сортировки
        order = self.request.query_params.get('order')
        if order:
            if order.endswith('contractor_title'):
                prefix = '-' if order.startswith('-') else ''
                queryset = queryset.order_by(f'{prefix}contractor__title')
            else:
                queryset = queryset.order_by(order)

        # Обрабатываем параметры поиска
        number = self.request.query_params.get('number')
        if number:
            queryset = queryset.filter(pk=number)
        dt_start = self.request.query_params.get('dt_start')
        if dt_start:
            queryset = queryset.filter(dt_created__gte=dt_start)
        dt_end = self.request.query_params.get('dt_end')
        if dt_end:
            queryset = queryset.filter(dt_created__lte=dt_end)
        contractor = self.request.query_params.get('contractor')
        if contractor:
            queryset = queryset.filter(contractor=contractor)
        destination_type = self.request.query_params.get('destination_type')
        if destination_type:
            queryset = queryset.filter(destination_type=destination_type)
        apply_flag = self.request.query_params.get('apply_flag')
        if apply_flag:
            queryset = queryset.filter(apply_flag=apply_flag)

        return queryset


class DocumentItemViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentItemSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = DocumentItem.objects.all()
        document = self.request.query_params.get('document')
        if document:
            queryset = queryset.filter(document=document)
        return queryset


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def apply_document(request, document_id):
    document = Document.objects.filter(pk=document_id).first()
    if not document:
        return Response({'error': f'Документ с номером {document_id} не найден'}, status=status.HTTP_400_BAD_REQUEST)
    if document.apply_flag:
        return Response({'error': f'Документ с номером {document_id} уже проведен'}, status=status.HTTP_400_BAD_REQUEST)

    document_items = DocumentItem.objects.filter(document=document)
    if document.destination_type == Document.RECEIPT:
        for document_item in document_items:
            storage_item = StorageItem.objects.filter(product_id=document_item.product_id).first()
            if storage_item:
                storage_item.count += document_item.count
                storage_item.save()
            else:
                StorageItem.objects.create(product=document_item.product, count=document_item.count)
        document.apply_flag = True
        document.save()

    elif document.destination_type == Document.EXPENSE:
        # TODO Вставить код проведения расходного документа
        pass

    return Response(status=status.HTTP_200_OK)
