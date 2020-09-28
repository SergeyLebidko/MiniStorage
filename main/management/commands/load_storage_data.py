import random
from django.core.management.base import BaseCommand
from main.models import Product, Storage, Operation


class Command(BaseCommand):

    def handle(self, *args, **options):
        products = Product.objects.all()
        if not products:
            print('Справочник Товары пуст. Перед выполнением команды заполните справочник.')
            return

        data = []
        for product in products:
            data.append(Storage(product=product, count=random.randint(1, 1000)))
        Storage.objects.bulk_create(data)

        Operation.objects.create(
            username='- Администратор системы -',
            operation=f'Командой load_storage_data добавлено наименований товаров на склад: {len(products)}'
        )
        print(f'Добавлено наименований на склад: {len(products)}')
