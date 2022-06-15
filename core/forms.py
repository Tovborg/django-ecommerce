from unittest.util import _MAX_LENGTH
from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PAYMENT_CHOICES = (
    ('P', 'PayPal'),
    ('S', 'Stripe')

)


class CheckoutForm(forms.Form):
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': '1234 Main'
    }))
    apartment_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Apartment or Suite'
    }))
    country = CountryField(blank_label='(select country)').formfield(
        widget=CountrySelectWidget(attrs={
            'class': 'form-select'
        }))
    zip = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    same_shipping_address = forms.BooleanField(required=False)
    save_info = forms.BooleanField(required=False)
    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)


class ReviewForm(forms.Form):
    reviewer = forms.CharField(max_length=200)
    stars = forms.IntegerField(max_value=5, min_value=1)
    review_text = forms.Textarea()


class ContactForm(forms.Form):
    first_name = forms.CharField(max_length=200)
    last_name = forms.CharField(max_length=200)
    phone_number = forms.CharField(max_length=200)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)

# Create coupon code form
class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code',
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2'
    }))
