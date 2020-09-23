from django.core.management.base import BaseCommand
from main.models import Contractor

test_data = [
    ('ООО Рога и копыта', Contractor.ENTITY),
    ('ОАО Газпром', Contractor.ENTITY),
    ('Sharif Industries', Contractor.ENTITY),
    ('Travor Philips Inc.', Contractor.INDIVIDUAL),
    ('ИП Дрищухин', Contractor.INDIVIDUAL),
    ('Digital Super Design', Contractor.ENTITY),
    ('NASA', Contractor.ENTITY),
    ('Microsoft', Contractor.ENTITY),
    ('Google Inc.', Contractor.ENTITY),
    ('Mafia boy', Contractor.INDIVIDUAL),
    ('ИП Пиписян А.Р.', Contractor.ENTITY)
]


class Command(BaseCommand):

    def handle(self, *args, **options):
        Contractor.objects.all().delete()
        data = []
        for title, category in test_data:
            data.append(Contractor(title=title, category=category))

        Contractor.objects.bulk_create(data)
        print(f'Создано записей: {len(test_data)}')
