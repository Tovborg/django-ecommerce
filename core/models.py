from datetime import date, datetime
from math import floor
from django.db import models
from django.conf import settings
from django.forms import IntegerField
from django.shortcuts import reverse
from core.forms import SHIPPING_CHOICES
from django_countries import Countries
from django_countries.fields import CountryField
from django.core import validators
from stripe import Product
from django.core.exceptions import ObjectDoesNotExist
# Create your models here.

CATEGORY_CHOICES = (
    ('S', 'Shirt'),
    ('SW', 'Sport wear'),
    ('OW', 'Outwear')
)

LABEL_CHOICES = (
    ('NC', 'New collection'),
    ('T', 'Trending'),
    ('OBG', 'Old but gold')
)


FEATURED_PRODUCTS_CHOICES = (
    ('NA', 'New arrival'),
    ('BS', 'Best selling'),
    ('OS', 'On sale'),
    ('FY', 'For you')
)

SHIPPING_CHOICES = (
    ('U', 'UPS'),
    ('F', 'FedEx'),
    ('D', 'DHL'),
)


class to_contact(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return self.first_name


class Size(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=20)
    field_name = models.CharField(max_length=20, default='default')

    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.CharField(
        max_length=70,
        verbose_name='Product Name'
    )
    price = models.FloatField(
        verbose_name='Price'
    )
    sizes = models.ManyToManyField(Size, blank=True)
    discount_price = models.FloatField(blank=True, null=True)
    category = models.ManyToManyField(Category)
    label = models.CharField(choices=LABEL_CHOICES, max_length=4)
    home_page_image = models.ImageField(
        upload_to='uploads/', blank=True, null=True)
    shop_grid_image = models.ImageField(
        upload_to='uploads/', blank=True, null=True)

    slug = models.SlugField()
    description = models.TextField(
        max_length=190,
        verbose_name='Description'
    )
    featured = models.BooleanField(default=False)
    times_ordered = models.IntegerField(default=1)
    featured_products = models.CharField(
        choices=FEATURED_PRODUCTS_CHOICES, max_length=10, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    color = models.ManyToManyField(Color)

    def get_date(self):
        return self.date_added.strftime('%b %d %Y')

    def __str__(self):
        return self.name

    def get_ajax_add_to_cart_url(self):
        return reverse("core:ajax-add-cart-item", kwargs={'slug': self.slug})

    def get_absolute_url(self):
        return reverse("core:product-page", kwargs={'slug': self.slug})

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={'slug': self.slug})

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={'slug': self.slug})

    def get_add_to_wishlist_url(self):
        return reverse("core:add-to-wishlist", kwargs={'slug': self.slug})

    def get_remove_from_wishlist_url(self):
        return reverse("core:remove-from-wishlist", kwargs={'slug': self.slug})

    def get_discount_percentage(self):
        return round((1 - (self.discount_price / self.price)) * 100)

    def get_average_rating(self):
        # get all reviews for this product
        reviews = Reviews.objects.filter(item=self)
        ratings = []
        # get the average rating
        if reviews.exists():
            if reviews.count() > 0:
                for review in reviews:
                    ratings.append(review.stars)
                return floor(sum(ratings) / len(ratings))
            else:
                return 0
        else:
            return 0

class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.name}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class CouponCode(models.Model):
    code = models.CharField(max_length=20)
    discount = models.IntegerField(default=0)
    valid_from = models.DateTimeField(auto_now_add=True)
    valid_to = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code
    
class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, null=True, blank=True)
    username = models.CharField(max_length=100)
    email = models.EmailField(max_length=150, null=True, blank=True)
    amount = models.IntegerField(default=0)
    items = models.ManyToManyField(
        to=OrderItem
    )
    discount = models.IntegerField(default=0, blank=True, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey(
        'BillingAddress', on_delete=models.SET_NULL, blank=True, null=True)
    order_identifier = models.IntegerField(
        default=0, null=True, blank=True)
    shipping_method = models.CharField(
        choices=SHIPPING_CHOICES, max_length=3, null=True, blank=True)

    def __str__(self):
        return self.username

    def get_subtotal(self):
        return sum([item.get_final_price() for item in self.items.all()])

    def get_total(self):
        #return total amount of the order, with 15% tax added, then minus total amount with discount in percentage if there is any discount applied to the order
        total = self.get_subtotal()
        total += total * 0.15
        if self.discount:
            total -= total * (self.discount / 100)
        return int(total)
        


    def get_discount_savings(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.discount:
            return (total * self.discount) / 100
        else:
            return total

    def get_tax(self):
        return int(self.get_subtotal() * 0.15)       
    #apply discount to the order
    def apply_discount(self):
        total = self.get_total()
        if self.discount:
            total -= total * (self.discount / 100)
        return total



class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.user.username


class Reviews(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    reviewer = models.CharField(max_length=100, null=True)
    stars = models.IntegerField(default=1)
    review_text = models.TextField(
        max_length=800,
        verbose_name='review content'
    )
    review_date = models.DateTimeField(auto_now_add=True)


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    items = models.ManyToManyField(Item, blank=True)

    def __str__(self):
        return str(self.user)

