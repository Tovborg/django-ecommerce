from django.core.management.base import BaseCommand
from core.models import FEATURED_PRODUCTS_CHOICES, Item, Color, Category
import random
import os

LABEL_CHOICES = (
    ('NC', 'New collection'),
    ('T', 'Trending'),
    ('OBG', 'Old but gold')
)

FEATURED_PRODUCTS_CHOICES

all_colors = []
for color in Color.objects.all():
    all_colors.append(color)

all_categories = []
for category in Category.objects.all():
    all_categories.append(category)

used_item_names = []
for item in Item.objects.all():
    used_item_names.append(item.name)





class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('number', type=int, nargs='+',
                            help='The number of items to create')
    def handle(self, *args, **kwargs):
        number_of_items = kwargs['number'][0]

        for i in range(number_of_items):
            name = f'Item-{i}'
            print(name)
            used_item_names.append(name)
            item = Item.objects.create(
                name=name,
                price=random.randint(100, 1000),
                label=random.choice(LABEL_CHOICES),
                #featured is a boolean field, so use random to determine whether it should be True or False
                featured=random.choice([True, False]),
                #home_page_image should be set to uploads/Webp.net-resizeimage_2_1svc0bM_OKCicII_gKnOY6R_Fz8Ygse.png
                home_page_image=f'uploads/Webp.net-resizeimage_2_1svc0bM_OKCicII_gKnOY6R_Fz8Ygse.png',
                #shop_grid_image should be set to uploads/Webp.net-resizeimage_ARxynLR_X0SO7qg_VSgascK_2nnVbjd.png
                shop_grid_image=f'uploads/Webp.net-resizeimage_ARxynLR_X0SO7qg_VSgascK_2nnVbjd.png',
                slug=name.replace(' ', '-').lower(),
                description=f'{name} is a cool item',
                # featured_products should only choose between the choices at index 0 in the tuple
                featured_products=random.choice(FEATURED_PRODUCTS_CHOICES)[0],
            )
            print(item)
            item.category.set(random.sample(all_categories, random.randint(1, len(all_categories))))
            for i in range(4):
                item.color.add(random.choice(all_colors))
            item.save()
        self.stdout.write(self.style.SUCCESS(f'Successfully created {number_of_items} items'))