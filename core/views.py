from importlib.metadata import metadata
from logging import exception
from unicodedata import category
from django.dispatch import receiver
from django.views.generic import ListView, DetailView, View, TemplateView, FormView
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from requests import request
from .models import *
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages
import json
from .forms import CheckoutForm, ReviewForm
from django.conf import settings  # new
from django.http import JsonResponse, HttpResponse, HttpResponseNotFound  # new
from django.views.decorators.csrf import csrf_exempt
import stripe
from django.contrib.auth.models import User
from django.db.models import F
from paypal.standard.forms import PayPalPaymentsForm
from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
import logging
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment
from paypalcheckoutsdk.orders import OrdersGetRequest
import sys


class PayPalClient:
    def __init__(self):
        self.client_id = "AQie0MKam6S2eIHkiYZTtoNxIJlNdVcD7pJN2aCp5wW-IRurKrBhsWDZ1Jmgnq_aNfyBCzg4FdS9uG5l"
        self.client_secret = "ECmL-BwSGdtgNmgebInz_RQ8TPUdnyxIdFJE9xjg2W6iHldKwql7bW4WrYnrB9UMVn_Ubgnvo5L3zzTf"
        self.environment = SandboxEnvironment(
            client_id=self.client_id, client_secret=self.client_secret)
        self.client = PayPalHttpClient(self.environment)


YOUR_DOMAIN = 'http://127.0.0.1:8000/'
stripe.api_key = settings.STRIPE_PRIVATE_KEY
logger = logging.getLogger(__name__)


class NavbarView(TemplateView):
    template_name = "updated-navbar.html"


class HomeView(View):
    def get(self, *args, **kwargs):
        try:
            featured_products = Item.objects.filter(
                featured=True
            )
            new_arrival = Item.objects.filter(
                featured_products='NA'
            )
            best_selling = Item.objects.filter(
                featured_products='BS'
            )
            on_sale = Item.objects.filter(
                featured_products='OS'
            )
            context = {
                'featured': featured_products,
                'new_arrival': new_arrival,
                'best_selling': best_selling,
                'on_sale': on_sale
            }
            return render(self.request, 'updated-home-page.html', context)
        except ObjectDoesNotExist:
            return render(self.request, 'updated-home-page.html')


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order_qs = Order.objects.filter(
                user=self.request.user, ordered=False)
            order = order_qs[0]
            products = order.items.filter(
                user=self.request.user, ordered=False)
            cart_order = Order.objects.get(
                user=self.request.user, ordered=False)
            form = CheckoutForm()

            context = {
                'form': form,
                'object': products,
                'order': cart_order,
            }

            return render(self.request, "checkout_page.html", context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("/")
        except IndexError:
            return redirect('core:home-page')

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                street_address = self.request.POST.get('street_address')
                apartment_address = self.request.POST.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip = self.request.POST.get('zip')
                payment_option = self.request.POST.get('payment_option')
                billing_address = BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip=zip
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                if payment_option == 'S':
                    return redirect('core:checkout')
            messages.warning(self.request, 'failed checkout')
            return redirect('core:checkout-page')
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("core:order-summary")


class ItemDetailView(DetailView):
    model = Item
    template_name = "product-page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item = self.get_object()
        context['reviews'] = Reviews.objects.filter(
            item=item
        )
        context['form'] = ReviewForm()
        return context

    def post(self, *args, **kwargs):

        if self.request.method == 'POST':
            reviewer = self.request.POST.get('reviewer')
            stars = self.request.POST.get('stars')
            review_text = self.request.POST.get('review_text')
            review = Reviews(
                item=self.get_object(),
                user=self.request.user,
                reviewer=reviewer,
                review_text=review_text,
                stars=stars
            )
            review.save()
            print('form was validated')
            return HttpResponse(json.dumps({'message': 'test'}))
        else:
            return HttpResponse('not a post request')


class ShirtView(ListView):
    def get(self, *args, **kwargs):

        shirt_items = Item.objects.filter(
            category='S'
        )
        context = {
            'items': shirt_items
        }
        if shirt_items.exists():
            return render(self.request, 'shirts.html', context)
        else:
            messages.info(
                self.request, "There are currently no items in this category")
            return redirect("/")


class SportWearsView(ListView):
    def get(self, *args, **kwargs):

        sportwears_items = Item.objects.filter(
            category='SW'
        )
        context = {
            'items': sportwears_items
        }
        if sportwears_items.exists():
            return render(self.request, 'sportwear.html', context)
        else:
            messages.info(
                self.request, "There are currently no items in this category")
            return redirect("/")


class OutwearView(ListView):
    def get(self, *args, **kwargs):

        outwear = Item.objects.filter(
            category='OW'
        )
        context = {
            'items': outwear
        }
        if outwear.exists():
            return render(self.request, 'outwear.html', context)
        else:
            messages.info(
                self.request, "There are currently no items in this category")
            return redirect("/")


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = OrderItem.objects.filter(
                user=self.request.user, ordered=False)
            cart_order = Order.objects.get(
                user=self.request.user, ordered=False)
            context = {'object': order, 'order': cart_order}
            return render(self.request, 'order_summary.html', context)

        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("/")


# Payments

# STRIPE PAYMENT

# Creates stripe checkout session
@csrf_exempt
def create_checkout_session(request):
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    order = order_qs[0]
    products = order.items.filter(user=request.user, ordered=False)
    order_items = []
    if products.count() > 0:
        for i in range(products.count()):
            if products[i].item.discount_price:
                price = products[i].item.discount_price
            else:
                price = products[i].item.price
            order_items.append({
                'price_data': {
                    'currency': 'dkk',
                    'product_data': {
                        'name': products[i].item.name,
                    },
                    'unit_amount': int(price) * 100,
                },
                'quantity': products[i].quantity,
            })
    print(order_items)
    session = stripe.checkout.Session.create(
        client_reference_id=request.user.id if request.user.is_authenticated else None,
        payment_method_types=['card'],
        metadata={
            "user": request.user
        },
        line_items=order_items,
        mode='payment',
        success_url=YOUR_DOMAIN,
        cancel_url=YOUR_DOMAIN,
    )
    # print(session)
    return redirect(session.url, code=303)


# Stripe webhook for handling events
@csrf_exempt
def webhook(request):
    payload = request.body
    event = None

    try:
        event = stripe.Event.construct_from(
            json.loads(payload), stripe.api_key
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)

    # Handle the event
    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object  # contains a stripe.PaymentIntent
        print('PaymentIntent was successful!')

    elif event.type == 'payment_method.attached':
        payment_method = event.data.object  # contains a stripe.PaymentMethod
        print('PaymentMethod was attached to a Customer!')
    elif event.type == 'checkout.session.completed':
        session = event['data']['object']
        price = session['amount_total'] / 100
        sessionID = session['id']
        print(session)
        customer_email = session["customer_details"]["email"]
        user = session['metadata']['user']
        order_qs = Order.objects.filter(username=user, ordered=False)
        order_qs.update(email=customer_email, amount=price,
                        description=sessionID, ordered=True)
        order = Order.objects.get(
            description=sessionID,
        )
        for item in order.items.all():
            items = item.item
            items.times_ordered = F('times_ordered') + item.quantity
            items.save()
            # ... handle other event types
    else:
        print('Unhandled event type {}'.format(event.type))

    return HttpResponse(status=200)

# STRIPE PAYMENTS END
# PAYPAL
@login_required
def payment_complete(request):
    PPClient = PayPalClient()

    body = json.loads(request.body)
    data = body["orderID"]
    user_id = request.user.id

    requestorder = OrdersGetRequest(data)
    response = PPClient.client.execute(requestorder)

    order_qs = Order.objects.filter(user=request.user, ordered=False)
    order_qs.update(
        email=response.result.payer.email_address,
        amount=int(float(response.result.purchase_units[0].amount.value)),
        description=data,
        ordered=True
    )

    return JsonResponse("Payment completed!", safe=False)


class PaypalSuccess(TemplateView):
    template_name = 'paypal_success.html'

# PAYPAL END
# Payments end


# Removes the whole items, AKA: sets quantity to zero and removes it
@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "This item was removed from your cart")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product-page", slug=slug)

    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product-page", slug=slug)


# Decreases quantity by one
@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(username=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
                order_item.delete()
                order.save()
                messages.info(request, "This item was removed from cart")
            messages.info(request, "This item quantity was updated")
            return redirect("core:checkout-page")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product-page", slug=slug)

    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product-page", slug=slug)


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("core:checkout-page")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("core:checkout-page")
    else:

        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user,
            ordered_date=ordered_date,
            username=request.user,
            order_identifier=Order.objects.all().last().order_identifier + 1
        )
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("core:checkout-page")


@login_required
def payment_finished(request):
    product = OrderItem.objects.filter(user=request.user, ordered=False)
    product.update(ordered=True)
    return redirect("core:home-page")


class OrderHistoryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        order = Order.objects.filter(
            user=self.request.user
        )
        context = {
            'object': order,
        }
        if order.count() == 0:
            messages.error(self.request, "You do not have an active order")
            return redirect("core:home-page")
        else:
            return render(self.request, 'order_history.html', context)
