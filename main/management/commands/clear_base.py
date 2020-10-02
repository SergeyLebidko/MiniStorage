from django.core.management.base import BaseCommand
from main.models import Product, Contractor, StorageItem, Document, Operation


def action():
    Document.objects.all().delete()
    StorageItem.objects.all().delete()
    Product.objects.all().delete()
    Contractor.objects.all().delete()
    Operation.objects.create(
        username='- Администратор системы -',
        operation='Командой clear_base выполнена очистка базы данных'
    )


class Command(BaseCommand):

    def handle(self, *args, **options):
        action()
        print('Очистка базы выполнена')
