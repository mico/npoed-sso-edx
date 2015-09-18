from django.core.management.base import BaseCommand
from apps.openedx_objects.tasks import get_edx_libraries

class Command(BaseCommand):
    help = 'Get objects from Open-EDX'

    def handle(self, *args, **options):
        get_edx_libraries()
        self.stdout.write('Done')

