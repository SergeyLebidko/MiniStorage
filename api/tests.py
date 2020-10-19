import random
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from main.models import Token, Product, Contractor, Document, DocumentItem, StorageItem

TOKEN = 'token'
BASE_PRICE = 1000
BASE_COUNT = 100


def create_products_and_contractors():
    for index in range(BASE_COUNT):
        Product.objects.create(title=f'Товар {index}', price=BASE_PRICE)
        Contractor.objects.create(title=f'Контрагент {index}', category=random.choice(Contractor.CONTRACTOR_CATEGORY))


def create_document(destination_type, apply_flag, create_storage_items, items_count=10, products_count=3):
    contractors = list(Contractor.objects.all())
    products = list(Product.objects.all())

    document = Document.objects.create(
        contractor=random.choice(contractors),
        destination_type=destination_type,
        apply_flag=apply_flag
    )
    random.shuffle(products)
    for index in range(items_count):
        DocumentItem.objects.create(document=document, product=products[index], count=products_count)
        if create_storage_items:
            StorageItem.objects.create(product=products[index], count=products_count)

    return document, items_count, products_count


class TestApi(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('test_user', password='password')
        Token.objects.create(user=cls.user, token=TOKEN)
        create_products_and_contractors()

    def setUp(self):
        self.client = client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=TOKEN)

    def test_apply_receipt_document(self):
        """Тестируем проведение приходного документа"""
        document, items_count, products_count = create_document(Document.RECEIPT, False, False)

        url = reverse('api:apply_document', kwargs={'document_id': document.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'Некорректный http-статус ответа')

        storage_items = StorageItem.objects.all()
        self.assertEqual(len(storage_items), items_count, 'Документ проведен некорректно')
        for storage_item in storage_items:
            self.assertEqual(storage_item.count, products_count, 'Документ проведен некорректно')

    def test_apply_expense_document(self):
        """Тестируем проведение расходного документа"""
        document, *_ = create_document(Document.EXPENSE, False, True)

        url = reverse('api:apply_document', kwargs={'document_id': document.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'Некорректный http-статус ответа')

        storage_items_count = StorageItem.objects.count()
        self.assertEqual(storage_items_count, 0, 'Документ проведен некорректно')

    def test_unapply_receipt_document(self):
        """Тестируем отмену проведения приходного документа"""
        document, *_ = create_document(Document.RECEIPT, True, True)

        url = reverse('api:unapply_document', kwargs={'document_id': document.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'Некорректный http-статус ответа')

        storage_items_count = StorageItem.objects.count()
        self.assertEqual(storage_items_count, 0, 'Отмена проведения документа прошла некорректно')

    def test_unapply_expense_document(self):
        """Тестируем отмену проведения расходного документа"""
        document, items_count, products_count = create_document(Document.EXPENSE, True, False)

        url = reverse('api:unapply_document', kwargs={'document_id': document.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'Некорректный http-статус ответа')

        storage_items = StorageItem.objects.all()
        self.assertEqual(len(storage_items), items_count, 'Отмена проведения документа прошла некорректно')
        for storage_item in storage_items:
            self.assertEqual(storage_item.count, products_count, 'Отмена проведения документа прошла некорректно')

    def test_apply_not_exist_document(self):
        """Тестируем невозможность проведения несуществующего документа"""
        url = reverse('api:apply_document', kwargs={'document_id': 1})
        response = self.client.post(url)
        msg = 'Удалось провести документ с некорректным номером'
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, msg)

    def test_unapply_not_exist_document(self):
        """Тестируем невозможность отмены проведения несуществующего документа"""
        url = reverse('api:unapply_document', kwargs={'document_id': 1})
        response = self.client.post(url)
        msg = 'Удалось отменить проведение документа с некорректным номером'
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, msg)

    def test_apply_applying_document(self):
        """Тестируем невозможность проведения уже проведенного документа"""
        document, *_ = create_document(Document.RECEIPT, True, True)
        url = reverse('api:apply_document', kwargs={'document_id': document.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'Удалось провести уже проведенный документ')

    def test_unapply_unapplying_document(self):
        """Тестируем невозможность отмены проведения документа, который не является проведенным"""
        document, *_ = create_document(Document.RECEIPT, False, True)
        url = reverse('api:unapply_document', kwargs={'document_id': document.pk})
        response = self.client.post(url)
        msg = 'Удалось отменить проведение не проведенного документа'
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, msg)

    def test_apply_incorrect_expense_document(self):
        """Тестируем невозможность проведения некорректного расходного документа"""
        document, *_ = create_document(Document.EXPENSE, False, False)
        url = reverse('api:apply_document', kwargs={'document_id': document.pk})
        response = self.client.post(url)
        msg = 'Удалось провести расходный документ при отстутсвии товаров на складе'
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, msg)

    def test_unapply_incorrect_receipt_document(self):
        """Тестируем невозможность отмены проведения приходного документа при отсутствии товаров на складе"""
        document, *_ = create_document(Document.RECEIPT, True, False)
        url = reverse('api:unapply_document', kwargs={'document_id': document.pk})
        response = self.client.post(url)
        msg = 'Удалось отменить проведение приходного документа при отстутвии товаров на складе'
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, msg)

    def test_remove_markup_object(self):
        """Тестируем удаление помеченных объектов"""
        document, items_count, _ = create_document(Document.RECEIPT, False, True)

        # Помечаем объекты на удаление
        document.to_remove = True
        document.save()
        StorageItem.objects.all().update(to_remove=True)
        products_ids = DocumentItem.objects.values_list('product_id', flat=True)
        Product.objects.filter(id__in=products_ids).update(to_remove=True)

        document.contractor.to_remove = True
        document.contractor.save()

        url = reverse('api:remove_marked_objects')
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK, 'Некорректный http-статус объекта')

        # Проверяем, действиетельно ли объекты были удалены
        document_items_count = DocumentItem.objects.count()
        self.assertEqual(document_items_count, 0, 'Товары в документе, помеченном на удаление не были удалены')

        documents_count = Document.objects.count()
        self.assertEqual(documents_count, 0, 'Помеченный на удаление документ не был удален')

        storage_items_count = StorageItem.objects.count()
        self.assertEqual(storage_items_count, 0, 'Помеченные на удаление остатки на складе не были удалены')

        contractors_count = Contractor.objects.count()
        self.assertEqual(contractors_count, BASE_COUNT - 1, 'Помеченный на удаление контрагент не был удален')

        products_count = Product.objects.count()
        self.assertEqual(products_count, BASE_COUNT - items_count, 'Помеченные на удаление товары не были удалены')

    def test_impossibility_remove_markup_objects(self):
        """Тестируем невозможность удаления объектов, на которые есть ссылки"""
        document, *_ = create_document(Document.RECEIPT, True, True)

        document.contractor.to_remove = True
        document.contractor.save()

        products_ids = DocumentItem.objects.values_list('product_id', flat=True)
        products_to_remove = Product.objects.filter(id__in=products_ids)
        products_to_remove.update(to_remove=True)

        url = reverse('api:remove_marked_objects')
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK, 'Некорректный http-статус объекта')

        products_count = Product.objects.count()
        contractors_count = Contractor.objects.count()

        msg = 'Помеченные на удаление товары были удалены, хотя на них были ссылки'
        self.assertEqual(products_count, BASE_COUNT, msg)

        msg = 'Помеченные на удаление контрагенты были удалены, хотя на них есть ссылки'
        self.assertEqual(contractors_count, BASE_COUNT, msg)

    def test_motion_report(self):
        """Тестируем корректность формирования отчета по движениям"""

        def get_view_results(url):
            rep_results = []
            rep_totals = None
            while url:
                response = self.client.get(url)
                rep_results.extend(response.json()['results'])
                if not rep_totals:
                    rep_totals = response.json()['totals']
                url = response.json()['next']

            return rep_results, rep_totals

        def test_function(rep_results, rep_totals, comparison_func, res_msg, totals_msg):
            document_items = DocumentItem.objects.select_related('document', 'product').all()
            total_receipt_count = total_receipt_sum = total_expense_count = total_expense_sum = 0
            for rep_result in rep_results:
                pk = rep_result['id']
                receipt_count = receipt_sum = expense_count = expense_sum = 0
                for document_item in document_items:
                    if comparison_func(document_item, pk):
                        continue
                    if document_item.document.destination_type == Document.RECEIPT:
                        receipt_count += document_item.count
                        receipt_sum += document_item.count * document_item.product.price
                    if document_item.document.destination_type == Document.EXPENSE:
                        expense_count += document_item.count
                        expense_sum += document_item.count * document_item.product.price

                expected_result = {
                    'id': pk,
                    'title': rep_result['title'],
                    'receipt_count': receipt_count,
                    'receipt_sum': receipt_sum,
                    'expense_count': expense_count,
                    'expense_sum': expense_sum
                }
                self.assertEqual(rep_result, expected_result, res_msg)

                total_receipt_count += receipt_count
                total_receipt_sum += receipt_sum
                total_expense_count += expense_count
                total_expense_sum += expense_sum

            expected_totals = {
                'total_receipt_count': total_receipt_count,
                'total_receipt_sum': total_receipt_sum,
                'total_expense_count': total_expense_count,
                'total_expense_sum': total_expense_sum
            }
            self.assertEqual(rep_totals, expected_totals, totals_msg)

        for document_type in [Document.RECEIPT, Document.EXPENSE]:
            for _ in range(10):
                create_document(document_type, True, False)

        # Тестируем отчет по товарам
        report_results, report_totals = get_view_results(reverse('api:motion_report') + '?report_type=products')
        test_function(
            report_results,
            report_totals,
            comparison_func=lambda document_item, pk: document_item.product_id != pk,
            res_msg='Отчет по движению товаров не корректен',
            totals_msg='Некорректные итоги в отчете по движению товаров'
        )

        # Тестируем отчет по операциям с контрагентами
        report_results, report_totals = get_view_results(reverse('api:motion_report') + '?report_type=contractors')
        test_function(
            report_results,
            report_totals,
            comparison_func=lambda document_item, pk: document_item.document.contractor_id != pk,
            res_msg='Отчет по движению контрагентов не корректен',
            totals_msg='Некорректные итоги в отчете по движению контрагентов'
        )
