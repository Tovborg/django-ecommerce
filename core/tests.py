from django.test import TestCase
from .models import *
import os


# print(item_colors)
product = Item.objects.get(name='Item-73')
reviews = Reviews.objects.filter(item=product)
ratings = []
if reviews.count() > 0:
    for review in reviews:
        ratings.append(review.stars)
    print(ratings)
    print(floor(sum(ratings) / len(ratings)))
else:
    print(0)