from django.core.management.base import BaseCommand
from .clear_base import action as clear_base_action
from .load_test_products import action as load_test_products_action
from .load_test_contractors import action as load_test_contractors_action
from .load_storage_items import action as load_storage_items_action
from .load_test_documents import action as load_test_documents_action


class Command(BaseCommand):

    def handle(self, *args, **options):
        print('Начинаю работу...')
        clear_base_action()
        load_test_products_action()
        load_test_contractors_action()
        load_storage_items_action()
        load_test_documents_action()
        print('Создание тестовой базы данных завершено...')
