from itertools import product
from locale import currency
from pipes import Template
from typing import ItemsView
from django.views.generic import ListView, DetailView, View, TemplateView, FormView
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from .models import *
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages
import json
from .forms import CheckoutForm, ReviewForm, ContactForm, CouponForm
from django.conf import settings  # new
from django.http import JsonResponse, HttpResponse, HttpResponseNotFound  # new
from django.views.decorators.csrf import csrf_exempt
import stripe
from django.contrib.auth.models import User
from django.db.models import F, Q
import logging
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment
from paypalcheckoutsdk.orders import OrdersGetRequest
from django.core.paginator import Paginator


class PayPalClient:
    def __init__(self):
        self.client_id = settings.PAYPAL_CLIENT_ID
        self.client_secret = settings.PAYPAL_SECRET_ID
        self.environment = SandboxEnvironment(
            client_id=self.client_id, client_secret=self.client_secret)
        self.client = PayPalHttpClient(self.environment)


YOUR_DOMAIN = 'http://127.0.0.1:11000/'
stripe.api_key = 'sk_test_51Kw5nlHaBBAjc5DSo1oyLsNtPTw2rFaUU7PdSqaiX4IDryTAqLcVZ4X1utQT6hwCL8urhiQaU18arBedsmAvk2QH00jxEvRxw0'
logger = logging.getLogger(__name__)


def entry_not_found(request, exception):
    context = {}
    if request.user.is_authenticated:
        order_qs = Order.objects.filter(
            user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            products = order.items.filter(
                ordered=False, user=request.user)
            context['products'] = products
    return render(request, '404.html', context)


class HomeView(View):
    def get(self, *args, **kwargs):
        try:
            host = self.request.get_host()
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
                'on_sale': on_sale,
                'host': host,
            }
            if self.request.user.is_authenticated:
                order_qs = Order.objects.filter(
                    user=self.request.user, ordered=False)
                if order_qs.exists():
                    order = order_qs[0]
                    products = order.items.filter(
                        ordered=False, user=self.request.user)
                    context['products'] = products
                    context['order'] = order

            return render(self.request, 'updated-home-page.html', context)
        except ObjectDoesNotExist:
            return render(self.request, 'updated-home-page.html')


class CheckoutView(LoginRequiredMixin, View):
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
            # add coupon form
            coupon_form = CouponForm()

            context = {
                'form': form,
                'object': products,
                'order': cart_order,
                'coupon_form': coupon_form,
            }
            if self.request.user.is_authenticated:
                order_qs = Order.objects.filter(
                    user=self.request.user, ordered=False)
                if order_qs.exists():
                    order = order_qs[0]
                    products = order.items.filter(
                        ordered=False, user=self.request.user)
                    order_items = OrderItem.objects.filter(
                        ordered=False, user=self.request.user)
                    context['products'] = products
            return render(self.request, "checkout_page.html", context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("/")
        except IndexError:
            return redirect('core:home-page')

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            print('posting')
            order = Order.objects.get(user=self.request.user, ordered=False)
            print(order)
            if self.request.method == 'POST':
                street_address = self.request.POST.get('street_address')
                apartment_address = self.request.POST.get('apartment_address')
                country = self.request.POST.get('country')
                zip = self.request.POST.get('zip')
                payment_option = self.request.POST.get('payment_option')
                shipping_option = self.request.POST.get('shipping')
                email = self.request.POST.get('email')
                billing_address = BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip=zip
                )
                order_updated = Order.objects.get(
                    user=self.request.user, ordered=False).update(
                    billing_address=billing_address,
                    email=email,
                )
                order_updated.save()
                order.save()
                billing_address.save()
                order.billing_address = billing_address
                order.save()
            messages.warning(self.request, 'failed checkout')
            return redirect('core:checkout-page')
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("core:home-page")


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
        if self.request.user.is_authenticated:
            order_qs = Order.objects.filter(
                user=self.request.user, ordered=False)
            if order_qs.exists():
                order = order_qs[0]
                context['order'] = order
                context['items'] = order.items.filter(
                    ordered=False, user=self.request.user)

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

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def applyCoupon(request):
    print(request.method)
    cart_order = Order.objects.get(
                user=request.user, ordered=False)
    response_data = {}
    if request.method == 'POST':

        coupon_form = CouponForm(request.POST or None)
        request_getdata = request.POST.get('coupon_code', None)
        print(request_getdata)

        try: 
   
            coupon_qs = CouponCode.objects.filter(code=request_getdata)
            if coupon_qs.exists():
                coupon_code = coupon_qs.first()
                if coupon_code.active:
                    cart_order.discount = coupon_code.discount
                    cart_order.save()
                    print(cart_order.discount)
                    response_data['success'] = True
                    response_data['amount_saved'] = cart_order.get_discount_savings()
                    response_data['discount'] = cart_order.discount
                    response_data['total_amount'] = cart_order.get_total()
                    print(cart_order.get_total())
                    response_data['message'] = 'Coupon code applied successfully!'
                    
                else:
                    response_data['success'] = False
                    response_data['message'] = 'Coupon code is not active!'
        except ObjectDoesNotExist:
            response_data['error'] = 'Coupon does not exist'
        
        return JsonResponse(response_data)
    get_response = {}
    if request.method == 'GET':
        total = cart_order.get_total()
        get_response['total'] = total
        return JsonResponse(get_response)



def billing_address(request):
    cart_order = Order.objects.get(
                user=request.user, ordered=False)
    response_data = {}
    if request.method == 'POST':
        street_address = request.POST.get('street_address', None)
        apartment_address = request.POST.get('apartment_address', None)
        country = request.POST.get('country', None)
        zip = request.POST.get('zipcode', None)
        print(zip)
        email = request.POST.get('email', None)
        print(email)
        shipping_method = request.POST.get('shipping_options', None)
        print(shipping_method)
        billing_address = BillingAddress(
            user=request.user,
            street_address=street_address,
            apartment_address=apartment_address,
            country=country,
            zip=zip
        )
        
        billing_address.save()
        cart_order.billing_address = billing_address
        cart_order.save()
        cart_order.email = email
        cart_order.save()
        response_data['success'] = True
        response_data['message'] = 'Billing address added successfully!'
        return JsonResponse(response_data)
    else:
        return JsonResponse('not a post request')
# Payments

# STRIPE PAYMENT

# Creates stripe checkout session




class checkout(TemplateView):
    template_name = "checkout.html"

@csrf_exempt    
def create_payment(request):
    order = Order.objects.get(user=request.user, ordered=False)
    amount = order.get_total()
    print(amount)
    print('block executed')
    try:
        data = json.loads(request.body)
        print(data)
        # Create a PaymentIntent with the order amount and currency
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),
            currency='eur',
            automatic_payment_methods={
                'enabled': True,
            },
            metadata={
                'user': request.user
            },
        )
        print(intent)
        return JsonResponse({'clientSecret': intent['client_secret']})
    except Exception as e:
        return JsonResponse(json.dumps(str(e)), safe=False)


    

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
        payment_intent = event.data.object
        print(payment_intent)
        session = event['data']['object']
        price = session['amount'] / 100
        sessionID = session['id']
        # print(sessionID)
        user = session['metadata']['user']
        # print(user)
        order_qs = Order.objects.filter(username=user, ordered=False)
        order_qs.update(amount=price,
                        description=sessionID, ordered=True)
        order = Order.objects.get(
            description=sessionID,
        )
        for item in order.items.all():
            items = item.item
            items.times_ordered = F('times_ordered') + item.quantity
            items.save()
            item.ordered = True
            item.save()

        
        
        

    elif event.type == 'payment_method.attached':
        payment_method = event.data.object  # contains a stripe.PaymentMethod
        print('PaymentMethod was attached to a Customer!')
    elif event.type == 'checkout.session.completed':
        print('Checkout session was completed!')
        session = event['data']
        price = session['amount'] / 100
        sessionID = session['id']
        print(session)
        user = session['metadata']['user']
        order_qs = Order.objects.filter(username=user, ordered=False)
        order_qs.update(amount=price,
                        description=sessionID, ordered=True)
        order = Order.objects.get(
            description=sessionID,
        )
        for item in order.items.all():
            items = item.item
            items.times_ordered = F('times_ordered') + item.quantity
            items.save()
            item.ordered = True
            item.save()
            # ... handle other event types
    else:
        print('Unhandled event type {}'.format(event.type))

    return HttpResponse(status=200)


# STRIPE PAYMENTS END
# PAYPAL
@login_required
def payment_complete(request):
    print('payment complete, block executed')
    PPClient = PayPalClient()

    body = json.loads(request.body)
    data = body["orderID"]
    user_id = request.user.id

    requestorder = OrdersGetRequest(data)
    response = PPClient.client.execute(requestorder)

    order_qs = Order.objects.filter(user=request.user, ordered=False)
    for item in order_qs[0].items.all():
        items = item.item
        items.times_ordered = F('times_ordered') + item.quantity
        items.save()
        item.ordered = True
        item.save()
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
    print(slug)
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    response_data = {}
    if request.method == "POST":
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
                response_data['Success'] = True
                response_data['message'] = 'Item removed from cart!'
                response_data['quantity'] = 0
                response_data['total'] = order.get_total()
                messages.info(request, "This item was removed from your cart")
                return JsonResponse(response_data)
                
                
            else:
                messages.info(request, "This item was not in your cart")
                return redirect("core:product-page", slug=slug)

        else:
            messages.info(request, "You do not have an active order")
            return redirect("core:product-page", slug=slug)
    else:
        return JsonResponse("Not a post request", safe=False)


# Decreases quantity by one
@login_required
def remove_single_item_from_cart(request, slug):
    print(slug)
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(username=request.user, ordered=False)
    response_data = {}
    if request.method == "POST":
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
                response_data['success'] = True
                response_data['message'] = "This item quantity was updated"
                response_data['quantity'] = order_item.quantity
                response_data['total'] = order.get_total()
                if order.items.count() == 0:
                    response_data['empty'] = True
                else:
                    response_data['empty'] = False
                return JsonResponse(response_data)
            else:
                messages.info(request, "This item was not in your cart")
                return redirect("core:product-page", slug=slug)

        else:
            messages.info(request, "You do not have an active order")
            return redirect("core:product-page", slug=slug)
    else:
        return JsonResponse('Request must be POST.', safe=False)


def AjaxAddToCart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    response_data = {}
    if request.method == "POST":
        if order_qs.exists():
            order = order_qs[0]
            if order.items.filter(item__slug=item.slug).exists():
                order_item.quantity += 1
                order_item.save()
                response_data['success'] = True
                response_data['message'] = "This item quantity was updated"
                response_data['quantity'] = order_item.quantity
                response_data['total'] = order.get_total()
                response_data['empty'] = False
                response_data['items'] = order.items.count()
                return JsonResponse(response_data)
            else:
                return JsonResponse("This item was not in your cart", safe=False)
        else:
            return JsonResponse("You do not have an active order, please add items via the homepage to create an order", safe=False)
    else:
        return JsonResponse("Not a post request", safe=False)

        

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
        )
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("core:checkout-page")

# rewrite the above function to use AJAX
def add_to_cart_ajax(request, slug):
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
            return JsonResponse({"success": True, "message": "This item quantity was updated", "quantity": order_item.quantity, "total": order.get_total(), "operation": "increase_quantity"})
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return JsonResponse({"success": True, "message": "This item was added to your cart", "quantity": order_item.quantity, "total": order.get_total(), "operation": "create_new_item"})
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user,
            ordered_date=ordered_date,
            username=request.user,
        )
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return JsonResponse({"success": True, "message": "This item was added to your cart", "quantity": order_item.quantity, "total": order.get_total(), "operation": "create_order"})

@login_required
def payment_finished(request):
    product = OrderItem.objects.filter(user=request.user, ordered=False)
    product.update(ordered=True)
    return redirect("core:home-page")


# Wishlist functionality


class WishListView(LoginRequiredMixin, ListView):
    def get(self, *args, **kwargs):
        wishlist_qs = Wishlist.objects.filter(
            user=self.request.user
        )
        if wishlist_qs.exists():
            wishlist = wishlist_qs[0]
            wishlist_items = wishlist.items.all()

            context = {
                'object': wishlist_items,
            }
            if self.request.user.is_authenticated:
                order_qs = Order.objects.filter(
                    user=self.request.user, ordered=False)
                if order_qs.exists():
                    order = order_qs[0]
                    products = order.items.filter(
                        ordered=False, user=self.request.user)
                    order_items = OrderItem.objects.filter(
                        ordered=False, user=self.request.user)
                    context['products'] = products
                    context['order'] = order
            return render(self.request, "wish-list.html", context)
        else:
            return redirect('core:home-page')


@login_required
def add_to_wishlist(request, slug):
    item = get_object_or_404(Item, slug=slug)
    wishlist_qs = Wishlist.objects.filter(
        user=request.user
    )
    if wishlist_qs.exists():
        wishlist = wishlist_qs[0]
        if wishlist.items.filter(slug=item.slug).exists():
            return redirect('core:wishlist')
        else:
            wishlist.items.add(item)
            return redirect('core:wishlist')
    else:
        create_wishlist = Wishlist.objects.create(
            user=request.user,
        )
        create_wishlist.items.add(item)
        return redirect('core:wishlist')


@login_required
def remove_from_wishlist(request, slug):
    item = get_object_or_404(Item, slug=slug)
    wishlist_qs = Wishlist.objects.filter(
        user=request.user
    )
    if wishlist_qs.exists():
        wishlist = wishlist_qs[0]
        if wishlist.items.filter(slug=item.slug).exists():
            wishlist.items.remove(item)
            return redirect('core:wishlist')
        else:
            return redirect('core:home-page')
    else:
        return redirect('core:home-page')


def is_valid_queryparam(param):
    return param != '' and param is not None


def ShopGrid(request):
    all_items = Item.objects.all()
    categories = Category.objects.all()
    title_contains_query = request.GET.get('searchwidget1')
    title_exact_query = request.GET.get('searchwidget1')
    pricemin = request.GET.get('minprice1')
    pricemax = request.GET.get('maxprice1')
    color_items = Item.objects.all()

    used_colors = []
    item_colors = []

    for item in Item.objects.all():
        for color in item.color.all():
            item_colors.append(color)
            if color not in used_colors:
                used_colors.append(color)
    # used_colors = []
    
    # # print(all_items)
    # for item in all_items:
    #     for color in item.color.all():
    #         # print(color)
    #         if color not in used_colors:
    #             used_colors.append((color.name, color.code))
    # colors = used_colors[::-6]
    """
    Loop through all the colors and use the color name with request.GET.get(color name) and check if its on and if so filter the items by that color
    """
    for color in used_colors:
        # print(request.GET.get('{}'.format(color[0])))
        if request.GET.get('{}'.format(color.name)) == 'on':
            all_items = color_items.filter(color__name=color.name)
            # print(all_items)

    

    # print(colors)

    for category in categories:
        category.field_name = request.GET.get(category.name)
        if is_valid_queryparam(category.field_name):
            all_items = all_items.filter(category=category)
            page_obj = all_items.filter(category=category)

    for color in used_colors:
        color_name = color.name
        color_code = color.code
        color_field_name = request.GET.get(color_name)
        pagination = Paginator(all_items, 8)
        page_number = request.GET.get('page')
        page_obj = pagination.get_page(page_number)

        if is_valid_queryparam(color_field_name):
            all_items = all_items.filter(color__name=color_name)
            # print(all_items)
            page_obj = all_items.filter(color__name=color_name)
    if is_valid_queryparam(title_contains_query):
        all_items = all_items.filter(name__icontains=title_contains_query)
        page_obj = all_items.filter(name__icontains=title_contains_query)
    elif is_valid_queryparam(title_exact_query):
        all_items = all_items.filter(name__iexact=title_exact_query)
        page_obj = all_items.filter(name__iexact=title_exact_query)
    if is_valid_queryparam(pricemin):
        all_items = all_items.filter(price__gte=pricemin)
        page_obj = all_items.filter(price__gte=pricemin)
    if is_valid_queryparam(pricemax):
        all_items = all_items.filter(price__lt=pricemax)
        page_obj = all_items.filter(price__lt=pricemax)
    # print(page_obj)
    context = {
        'object': all_items,
        'categories': categories,
        'colors': used_colors,  # colors
        'page_obj': page_obj  # pagination
    }
    if request.user.is_authenticated:
        order_qs = Order.objects.filter(
            user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            products = order.items.filter(
                ordered=False, user=request.user)
            context['products'] = products
            context['order'] = order

    return render(request, 'shop-grid.html', context)





class WomensView(ListView):
    def get(self, *args, **kwargs):
        all_items = Item.objects.filter(category__field_name='womens')
        pagination = Paginator(all_items, 8)
        page_number = self.request.GET.get('page')
        page_obj = pagination.get_page(page_number)
        context = {
            'object': all_items,
            'page_obj': page_obj,
        }
        if self.request.user.is_authenticated:
            order_qs = Order.objects.filter(
                user=self.request.user, ordered=False)
            if order_qs.exists():
                order = order_qs[0]
                products = order.items.filter(
                    ordered=False, user=self.request.user)
                context['products'] = products
                context['order'] = order
        return render(self.request, 'womens.html', context)


class MensView(ListView):
    def get(self, *args, **kwargs):
        all_items = Item.objects.filter(category__field_name='mens_jewellery')
        pagination = Paginator(all_items, 8)
        page_number = self.request.GET.get('page')
        page_obj = pagination.get_page(page_number)

        context = {
            'object': all_items,
            'page_obj': page_obj,
        }
        if self.request.user.is_authenticated:
            order_qs = Order.objects.filter(
                user=self.request.user, ordered=False)
            if order_qs.exists():
                order = order_qs[0]
                products = order.items.filter(
                    ordered=False, user=self.request.user)
                context['products'] = products
                context['order'] = order
        return render(self.request, 'mens.html', context)


class ContactView(View):
    def get(self, *args, **kwargs):
        context = {}
        if self.request.user.is_authenticated:
            order_qs = Order.objects.filter(
                user=self.request.user, ordered=False)
            if order_qs.exists():
                order = order_qs[0]
                products = order.items.filter(
                    ordered=False, user=self.request.user)
                order_items = OrderItem.objects.filter(
                    ordered=False, user=self.request.user)
                context['products'] = products
                context['order'] = order
        return render(self.request, 'contact.html', context)

    def post(self, *args, **kwargs):
        form = ContactForm(self.request.POST or None)
        if self.request.method == 'POST':
            first_name = self.request.POST.get('FirstName')
            last_name = self.request.POST.get('LastName')
            email = self.request.POST.get('EmailAddress')
            phone_number = self.request.POST.get('ContactNumber')
            message = self.request.POST.get('message')
            contact = to_contact(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone_number,
                message=message
            )
            print(first_name, last_name, email, phone_number, message)
            contact.save()

            return redirect('core:home-page')

