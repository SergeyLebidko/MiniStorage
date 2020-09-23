from django.core.management.base import BaseCommand
from main.models import Product, Contractor


class Command(BaseCommand):

    def handle(self, *args, **options):
        Product.objects.all().delete()
        Contractor.objects.all().delete()
        print('Очистка базы выполнена')
