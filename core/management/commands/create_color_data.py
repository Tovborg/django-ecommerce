from django.core.management.base import BaseCommand
from core.models import Color


# class Command(BaseCommand):
#     def handle(self, *args, **options):
#         with open('core/management/commands/colors.csv', 'r') as f:
#             for line in f:
#                 name_with_underscore = line.strip().split(',')
#                 Color.objects.create(
#                     name=name_with_underscore[1], code=name_with_underscore[2])
#         self.stdout.write(self.style.SUCCESS('Successfully created colors'))

#Create a tuple with the most classic colors with their name and hex code
classic_colors = (
    ('red', '#ff0000'),
    ('orange', '#ffa500'),
    ('yellow', '#ffff00'),
    ('green', '#008000'),
    ('blue', '#0000ff'),
    ('purple', '#800080'),
    ('brown', '#a52a2a'),
    ('black', '#000000'),
    ('white', '#ffffff'),
)


class Command(BaseCommand):
    def handle(self, *args, **options):
        for i in classic_colors:
            Color.objects.create(name=i[0], code=i[1])
        self.stdout.write(self.style.SUCCESS('Successfully created colors'))