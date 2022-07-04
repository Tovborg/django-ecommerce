from django.urls import path, include
from .views import *

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home-page'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product-page'),
    path('checkout/', CheckoutView.as_view(), name="checkout-page"),
    path('add-to-cart/<slug>/', add_to_cart, name="add-to-cart"),
    path('remove-from-cart/<slug>/', remove_from_cart, name="remove-from-cart"),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart,
         name="remove_single_item_from_cart"),
#     path('create-checkout-session/', create_checkout_session, name='checkout'),
    path('webhooks/stripe/', webhook, name="webhook"),
    path("payment_finished/", payment_finished, name="payment_finished"),
    path('paypal/payment_complete/', payment_complete, name="payment-complete"),
    path('paypal/success/', PaypalSuccess.as_view(), name="paypal-success"),
    path('wish-list/', WishListView.as_view(), name="wishlist"),
    path('add-to-wishlist/<slug>/', add_to_wishlist, name="add-to-wishlist"),
    path('remove-from-wishlist/<slug>/',
         remove_from_wishlist, name="remove-from-wishlist"),
    path('shop-grid/', ShopGrid, name="shop-grid"),
    path('womens/', WomensView.as_view(), name="womens"),
    path('mens/', MensView.as_view(), name="mens"),
    path('contact/', ContactView.as_view(), name="contact"),
    path('apply-coupon/', applyCoupon, name="apply-coupon"),
    path('checkout-test/', checkout.as_view(), name="checkout-test"),
    path('create-payment-intent/', create_payment, name="create-payment-intent"),
    path('send-billing-form/', billing_address, name="send-billing-form"),
    path('ajax-add-to-cart/<slug>/', AjaxAddToCart, name="ajax-add-to-cart"),
    path('ajax-add-cart-item/<slug>/', add_to_cart_ajax, name="ajax-add-cart-item"),
]

handler404 = 'core.views.entry_not_found'
