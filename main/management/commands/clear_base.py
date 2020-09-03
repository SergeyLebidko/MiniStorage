from django.core.management.base import BaseCommand
from main.models import Product


class Command(BaseCommand):

    def handle(self, *args, **options):
        Product.objects.all().delete()
        print('Очистка базы выполнена')
