import random
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from main.models import Token, Product, Contractor, Document, DocumentItem, StorageItem

TOKEN = 'token'
BASE_PRICE = 1000


def create_products_and_contractors():
    # Добавляем в базу товары и контрагентов
    for index in range(100):
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
