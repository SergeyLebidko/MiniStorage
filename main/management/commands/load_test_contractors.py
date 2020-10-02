from django.core.management.base import BaseCommand
from main.models import Contractor, Operation

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


def action():
    Contractor.objects.all().delete()
    data = []
    for title, category in test_data:
        data.append(Contractor(title=title, category=category))

    Contractor.objects.bulk_create(data)
    Operation.objects.create(
        username='- Администратор системы -',
        operation=f'Командой load_test_contractors создано {len(test_data)} записей о контрагентах'
    )


class Command(BaseCommand):

    def handle(self, *args, **options):
        action()
        print(f'Создано записей: {len(test_data)}')
