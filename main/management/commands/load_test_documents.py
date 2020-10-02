import random

from django.core.management.base import BaseCommand
from main.models import Product, Contractor, Document, DocumentItem


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            required=True,
            type=int,
            help='Количество создаваемых в базе документов'
        )

    def handle(self, *args, **options):
        count = options['count']

        contractors = list(Contractor.objects.all())
        products = list(Product.objects.all())
        if not contractors:
            print('В базу не добавлены контрагенты')
            return
        if not products:
            print('В базу не добавлены товары')
            return

        documents = []
        for _ in range(count):
            documents.append(Document.objects.create(
                contractor=random.choice(contractors),
                destination_type=random.choice([Document.RECEIPT, Document.EXPENSE])
            ))

        for document in documents:
            items_count = random.randint(1, 20)
            if items_count > len(products):
                items_count = len(products)

            random.shuffle(products)
            for index in range(items_count):
                DocumentItem.objects.create(document=document, product=products[index], count=random.randint(1, 50))

        print(f'Создано документов: {count}')
