import os
from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models.query_utils import DeferredAttribute
from django.db.models.deletion import ProtectedError
from django.db.models import Sum, F

from utils import get_username_for_operation, apply_expense_document, apply_receipt_document, unapply_receipt_document, \
    unapply_expense_document
from main.models import Product, Contractor, StorageItem, Document, DocumentItem, Operation
from .serializers import ProductSerializer, ContractorSerializer, StorageItemSerializer, OperationSerializer, \
    DocumentSerializer, DocumentItemSerializer
from .pagination import CustomPagination
from .authentication import TokenAuthentication
from utils import get_tmp_file_path
from main.management.commands.load_test_products import action


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
                print(main_fields_before)
                print(main_fields_after)

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


class DocumentViewSet(RegisteredViewSet):
    serializer_class = DocumentSerializer
    pagination_class = CustomPagination
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    model = Document
    model_verbose_name = 'Документ'

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
            dt_end += " 23:59:59"
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

    def create(self, request, *args, **kwargs):
        result = viewsets.ModelViewSet.create(self, request, *args, **kwargs)
        document_id = request.data.get('document')
        document = Document.objects.get(pk=document_id)
        document_item = DocumentItem.objects.get(pk=result.data['id'])
        Operation.objects.create(
            username=get_username_for_operation(request.user),
            operation=f'В документ {document} добавлен товар {document_item}'
        )
        return result

    def update(self, request, *args, **kwargs):
        document_item_id = kwargs.get('pk')
        document_item = DocumentItem.objects.filter(pk=document_item_id).first()
        result = viewsets.ModelViewSet.update(self, request, *args, **kwargs)

        if document_item:
            count_before = document_item.count
            count_after = result.data['count']
            if count_before != count_after:
                Operation.objects.create(
                    username=get_username_for_operation(request.user),
                    operation=f'В документе {document_item.document} изменено количество товара {document_item.product.title} '
                              f'(было {count_before}, стало {count_after})'
                )
        return result

    def destroy(self, request, *args, **kwargs):
        document_item_id = kwargs.get('pk')
        document_item = DocumentItem.objects.filter(pk=document_item_id).first()
        result = viewsets.ModelViewSet.destroy(self, request, *args, **kwargs)

        if document_item:
            Operation.objects.create(
                username=get_username_for_operation(request.user),
                operation=f'Из документа {document_item.document} удален товар {document_item}'
            )
        return result


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def apply_document(request, document_id):
    document = Document.objects.filter(pk=document_id).first()
    if not document:
        return Response({'error': f'Документ с номером {document_id} не найден'}, status=status.HTTP_400_BAD_REQUEST)
    if document.apply_flag:
        return Response({'error': f'Документ с номером {document_id} уже проведен'}, status=status.HTTP_400_BAD_REQUEST)

    # Проведение приходного документа
    if document.destination_type == Document.RECEIPT:
        apply_receipt_document(document)

    # Проведение расходного документа
    elif document.destination_type == Document.EXPENSE:
        try:
            apply_expense_document(document)
        except Exception as ex:
            return Response(
                {'error': f'Невозможно провести документ. Недостаточно товара на складе: {ex}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    # Если ошибок не возникло - помечаем документ как проведенный и регистрируем операцию
    document.apply_flag = True
    document.save()
    Operation.objects.create(
        username=get_username_for_operation(request.user),
        operation=f'Документ {document} проведен'
    )
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def unapply_document(request, document_id):
    document = Document.objects.filter(pk=document_id).first()
    if not document:
        return Response({'error': f'Документ с номером {document_id} не найден'}, status=status.HTTP_400_BAD_REQUEST)
    if not document.apply_flag:
        return Response({'error': f'Документ с номером {document_id} не проведен'}, status=status.HTTP_400_BAD_REQUEST)

    # Отменяем проведение приходного документа
    if document.destination_type == Document.RECEIPT:
        try:
            unapply_receipt_document(document)
        except Exception as ex:
            return Response(
                {'error': f'Невозможно отменить проведение документа. Недостаточно товара на складе: {ex}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    # Отменяем проведение расходного документа
    elif document.destination_type == Document.EXPENSE:
        unapply_expense_document(document)

    # Если ошибок не возникло - помечаем документ как не проведенный и регистрируем операцию
    document.apply_flag = False
    document.save()
    Operation.objects.create(
        username=get_username_for_operation(request.user),
        operation=f'Отменено проведение документа {document}'
    )
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def remove_marked_objects(request):
    result = []

    models_to_remove = [
        (StorageItem, 'Товары на складе', 'товар на складе'),
        (Document, 'Документы', 'документ'),
        (Product, 'Товары', 'товар'),
        (Contractor, 'Контрагенты', 'контрагент')
    ]
    for model, description, operation_description in models_to_remove:
        success_list = []
        fail_list = []
        objects_to_remove = model.objects.filter(to_remove=True)
        for obj in objects_to_remove:
            string_description = str(obj)
            try:
                obj.delete()
                success_list.append(string_description)
                Operation.objects.create(
                    username=get_username_for_operation(request.user),
                    operation=f'Удален {operation_description} {string_description}'
                )
            except ProtectedError:
                fail_list.append(string_description)
                Operation.objects.create(
                    username=get_username_for_operation(request.user),
                    operation=f'Не удалось удалить {operation_description} {string_description}'
                )
        if success_list or fail_list:
            result.append(
                {
                    'description': description,
                    'success_list': success_list,
                    'fail_list': fail_list
                }
            )

    return Response(data=result, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def import_products(request):
    uploaded_file = request.data['uploaded_file']
    path = get_tmp_file_path('uploaded_file.xlsx')
    with open(path, 'wb') as output_file:
        output_file.write(uploaded_file.read())

    try:
        created_records = action(file_path=path)
        Operation.objects.create(
            username=get_username_for_operation(request.user),
            operation=f'Импортировано товаров: {created_records}'
        )
    except Exception as ex:
        return Response(data=f'Ошибка при импорте: {ex}', status=status.HTTP_400_BAD_REQUEST)
    finally:
        os.remove(path)

    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def consolidated_report(request):
    product_count = Product.objects.count()
    contractor_count = Contractor.objects.count()
    storage_item_count = StorageItem.objects.count()

    product_count_field = F('count')
    product_price_field = F('product__price')

    total_cost = StorageItem.objects.aggregate(tc=Sum(product_count_field * product_price_field))['tc']

    data = {
        'product_count': product_count,
        'contractor_count': contractor_count,
        'storage_item_count': storage_item_count,
        'total_cost': total_cost
    }
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def products_report(request):
    documents = Document.objects.prefetch_related('documentitem_set').filter(apply_flag=True)

    dt_start = request.query_params.get('dt_start')
    if dt_start:
        documents = documents.filter(dt_updated__gte=dt_start)
    dt_end = request.query_params.get('dt_end')
    if dt_end:
        dt_end += ' 23:59:59'
        documents = documents.filter(dt_updated__lte=dt_end)

    document_items = DocumentItem.objects.filter(document__in=documents)
    receipt_items = document_items.filter(document__destination_type=Document.RECEIPT)
    expense_items = document_items.filter(document__destination_type=Document.EXPENSE)

    # Итоги по приходным документам
    receipt_items = receipt_items.values(
        'product_id',
        'product__title',
    ).order_by(
        'product_id'
    ).annotate(
        tc=Sum('count'),
        ts=Sum(F('count') * F('product__price'))
    ).order_by(
        'product__title'
    )

    # Итоги по расходным документам
    expense_items = expense_items.values(
        'product_id',
        'product__title',
    ).order_by(
        'product_id'
    ).annotate(
        tc=Sum('count'),
        ts=Sum(F('count') * F('product__price'))
    ).order_by(
        'product__title'
    )

    return Response(data={'result': 'Success!'}, status=status.HTTP_200_OK)
