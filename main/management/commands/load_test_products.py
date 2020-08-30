from django.core.management.base import BaseCommand
from django.conf import settings
from openpyxl import load_workbook
from main.models import Product


class Command(BaseCommand):

    def handle(self, *args, **options):
        file_path = str(settings.BASE_DIR) + '/test_data/products.xlsx'
        work_book = load_workbook(file_path)
        sheet = work_book.get_sheet_by_name('data')

        Product.objects.all().delete()
        data = []
        row = 1
        while True:
            title = sheet.cell(row=row, column=3).value
            price = sheet.cell(row=row, column=4).value
            if not title:
                break
            data.append(Product(title=title, price=price))
            row += 1

        Product.objects.bulk_create(data)
        print(f'Создано записей: {row - 1}')
