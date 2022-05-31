from django.urls import path, include
from .views import *

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home-page'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product-page'),
    path('checkout/', CheckoutView.as_view(), name="checkout-page"),
    path('order-summary/', OrderSummaryView.as_view(), name="order-summary"),
    path('add-to-cart/<slug>/', add_to_cart, name="add-to-cart"),
    path('remove-from-cart/<slug>/', remove_from_cart, name="remove-from-cart"),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart,
         name="remove_single_item_from_cart"),
    path('create-checkout-session/', create_checkout_session, name='checkout'),
    path('webhooks/stripe/', webhook, name="webhook"),
    path("payment_finished/", payment_finished, name="payment_finished"),
    path("order_history/", OrderHistoryView.as_view(), name="order_history"),
    path('paypal/payment_complete/', payment_complete, name="payment-complete"),
    path('paypal/success/', PaypalSuccess.as_view(), name="paypal-success")
]
