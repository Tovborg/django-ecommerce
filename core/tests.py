from django.test import TestCase
from .models import *
# Create your tests here.
all_items = Item.objects.all()

used_colors = []
for item in all_items:
    for color in item.color.all():
        if color not in used_colors:
            used_colors.append(color.name)
print(used_colors)

# print(data)
