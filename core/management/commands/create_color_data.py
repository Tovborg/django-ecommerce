from django.core.management.base import BaseCommand
from core.models import Color


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('core/management/commands/colors.csv', 'r') as f:
            for line in f:
                name_with_underscore = line.strip().split(',')
                Color.objects.create(
                    name=name_with_underscore[1], code=name_with_underscore[2])
        self.stdout.write(self.style.SUCCESS('Successfully created colors'))
