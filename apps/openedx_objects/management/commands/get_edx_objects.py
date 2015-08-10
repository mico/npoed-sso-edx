from django.core.management.base import BaseCommand
from apps.openedx_objects.tasks import get_edx_objects

class Command(BaseCommand):
    help = 'Get objects from Open-EDX'

    def handle(self, *args, **options):
        get_edx_objects()
        self.stdout.write('Done')
