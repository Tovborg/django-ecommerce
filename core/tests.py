from django.test import TestCase
from .models import *
# Create your tests here.
qs = Order.objects.filter(
    username="emiltovborg",
    ordered=True
)
print(qs[0].items.all()[0].item.price)
print(qs.count())

# print(data)
