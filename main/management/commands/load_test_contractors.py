from django.core.management.base import BaseCommand
from main.models import Contractor


class Command(BaseCommand):

    def handle(self, *args, **options):
        Contractor.objects.all().delete()
