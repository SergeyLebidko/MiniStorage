from django.core.management.base import BaseCommand
from main.models import Product, Contractor, Operation


class Command(BaseCommand):

    def handle(self, *args, **options):
        Product.objects.all().delete()
        Contractor.objects.all().delete()
        Operation.objects.create(
            username='- Администратор системы -',
            operation='Командой clear_base выполнена очистка базы данных'
        )
        print('Очистка базы выполнена')
