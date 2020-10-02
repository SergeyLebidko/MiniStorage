import random

from django.core.management.base import BaseCommand
from main.models import Product, Contractor, Document, DocumentItem, Operation


def action(count=150):
    contractors = list(Contractor.objects.all())
    products = list(Product.objects.all())
    if not contractors:
        raise Exception('В базу не добавлены контрагенты')
    if not products:
        raise Exception('В базу не добавлены товары')

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

    Operation.objects.create(
        username='- Администратор системы -',
        operation=f'Командой load_test_documents создано {count} документов'
    )


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
        try:
            action(count)
            print(f'Создано документов: {count}')
        except Exception as ex:
            print(ex)
