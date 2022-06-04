from django.contrib import admin
from stripe import Review
from .models import *
# Register your models here.
admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(Reviews)
admin.site.register(Wishlist)
