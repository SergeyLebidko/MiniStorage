from django.core.management.base import BaseCommand
from django.conf import settings
from openpyxl import load_workbook
from main.models import Product, Operation


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            help='Количество создаваемых в базе записей'
        )

    def handle(self, *args, **options):
        count = options['count']

        file_path = str(settings.BASE_DIR) + '/test_data/products.xlsx'
        work_book = load_workbook(file_path)
        sheet = work_book.get_sheet_by_name('data')

        Product.objects.all().delete()
        data = []
        row = 1
        while True:
            if count is not None and row > count:
                break
            title = sheet.cell(row=row, column=3).value
            price = sheet.cell(row=row, column=4).value
            if not title:
                break
            data.append(Product(title=title, price=price))
            row += 1

        Product.objects.bulk_create(data)
        Operation.objects.create(
            username='- Администратор системы -',
            operation=f'Командой load_test_products создано {row - 1} записей о товарах'
        )
        print(f'Создано записей: {row - 1}')
