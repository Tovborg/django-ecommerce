from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(Category)
admin.site.register(to_contact)
admin.site.register(CouponCode)
admin.site.register(BillingAddress)