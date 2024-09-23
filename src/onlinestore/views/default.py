from django.views.generic import View, TemplateView
from django.http import JsonResponse
from django.shortcuts import render
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils.text import capfirst
from django.urls import reverse
from django.db import transaction
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from cart.utils import sf_calculator
from onlinestore.utils import is_valid_username, check_sponsor_and_redirect, send_temporary_account_email

import random
import string
import requests

User = get_user_model()


class IndexView(TemplateView):
    template_name = 'index.html'

    def get(self, request, username=None, *args, **kwargs):

        # Redirect and register username to session if username is provided
        if username:
            return check_sponsor_and_redirect(request, username, 'home_view')

        # API URL to fetch products
        api_url = 'https://dashboard.twcako.com/shop/api/get-product/'

        try:
            # Make the API request
            response = requests.get(api_url, verify=False)
            response.raise_for_status()
            data = response.json()
            products = data.get("products", []) if data.get("success") else []
        except requests.exceptions.RequestException as e:
            # Handle API request errors
            return JsonResponse({'error': str(e)})

        user = request.user

        print(f'User: {user}')
        print(user.is_authenticated)

        # Get products in cart (assuming 'ordered_items_by_shop' is a session variable containing the cart items)
        ordered_items_by_shop = request.session.get('ordered_items_by_shop', {})
        products_in_cart = [item['product']['slug'] for shop in ordered_items_by_shop.values() for item in
                            shop['items']]

        guest_user_info = request.session.get('guest_user_data', {})
        new_guest_user = request.session.get('new_guest_user', False)

        # Convert products list to a list if it's a queryset or similar iterable
        products_list = list(products)

        random_products = random.sample(products_list, min(len(products_list), 4)) if products_list else []
        rand_on_sale_products = random.sample(products_list, min(len(products_list), 3)) if products_list else []
        rand_best_seller_products = random.sample(products_list, min(len(products_list), 3)) if products_list else []
        rand_top_rated_products = random.sample(products_list, min(len(products_list), 3)) if products_list else []

        subcategories_choices = [
            ('health_wellness', 'Health & Wellness'),
            ('healthy_beverages', 'Healthy Beverages'),
            ('intimate_care', 'Intimate Care'),
            ('bath_body', 'Bath & Body'),
            ('watches', 'Watches'),
            ('bags', 'Bags'),
            ('accessories', 'Accessories'),
        ]

        subcategories = [category[0] for category in subcategories_choices]
        filtered_products = [p for p in products_list if p['category_2'] in subcategories]
        subcategory_counts = {subcategory: sum(1 for p in filtered_products if p['category_2'] == subcategory) for
                              subcategory in subcategories}
        subcategory_counts_display = {
            subcategory: {
                'name': capfirst(
                    next((name for value, name in subcategories_choices if value == subcategory), 'Unknown')),
                'count': count
            } for subcategory, count in subcategory_counts.items()
        }

        context = {
            'title': "HOME",
            'username': guest_user_info.get('username'),
            'password': guest_user_info.get('password'),
            'email': guest_user_info.get('email'),
            'new_guest_user': new_guest_user,
            'has_existing_order': request.session.get('has_existing_order', False),
            'products': products,
            'random_products': random_products,
            'rand_on_sale_products': rand_on_sale_products,
            'rand_best_seller_products': rand_best_seller_products,
            'rand_top_rated_products': rand_top_rated_products,
            'categories': subcategory_counts_display,
            'is_authenticated': request.user.is_authenticated,
            'products_in_cart': products_in_cart,
        }

        if new_guest_user:
            del request.session['new_guest_user']

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'has_existing_order': request.session.get('has_existing_order', False),
                'email': guest_user_info.get('email'),
            })

        return render(request, self.template_name, context)


class ProductFunnelView(TemplateView):
    title = "Product Funnel"
    context = {'title': title}

    def get_template_names(self):
        product = self.kwargs.get('product', None)
        username = self.request.GET.get('username')
        if not is_valid_username(username):
            return ['404.html']
        else:
            self.request.session['funnel_referrer'] = username
            print(username)

        if product == 'barley-for-cancer':
            return ['funnels/products/barley/cancer.html']
        elif product == 'barley-for-diabetes':
            return ['funnels/products/barley/diabetes.html']
        elif product == 'barley-for-high-blood':
            return ['funnels/products/barley/high-blood.html']
        elif product == 'old-age':
            return ['funnels/products/fusion-coffee/old-age.html']
        elif product == 'weight-loss':
            return ['funnels/products/fusion-coffee/weight-loss.html']
        elif product == 'boost-coffee':
            return ['funnels/products/boost_coffee/index.html']
        else:
            return ['404.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.request.GET.get('username')
        product = self.kwargs.get('product')

        context.update({'username': username, 'product': product})

        return context


def generate_funnel_username(request):
    product = 'barley-for-cancer'
    username = request.user.username
    url = reverse('product_funnel_with_params', kwargs={'product': product})
    full_url = f"{url}?username={username}"
    return HttpResponseRedirect(full_url)


@transaction.atomic
def create_order(request):
    try:
        user = request.user
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        line1 = request.POST.get("line1")
        barangay = request.POST.get("barangay")
        city = request.POST.get("city")
        province = request.POST.get("province")
        region = request.POST.get("region")
        postcode = request.POST.get("postcode")
        message = request.POST.get("message")

        cod_amount = request.POST.get("bundle_price")
        total_quantity = request.POST.get("bundle_qty")
        supplier = "promo"  # Default supplier set to promo

        print(f"Creating order for user: {user}, Supplier: {supplier}")

        if user.is_authenticated:
            print(f"User {user.username} is authenticated.")
            existing_order = Order.objects.filter(user=user, supplier=supplier, complete=False).first()
            if existing_order:
                print(
                    f"Found existing incomplete order for user {user.username} with order ID: {existing_order.order_id}")
                order = existing_order
            else:
                print(f"No existing order found for user {user.username}. Creating new order.")
                default_address = Address.objects.filter(user=user, is_default=True).first()
                if not default_address:
                    return JsonResponse({'error': 'Default address not found for the user'}, status=400)
                region = default_address.region
                shipping_fee = sf_calculator(region=region, qty=total_quantity)

                order = Order.objects.create(
                    user=user,
                    supplier=supplier,
                    complete=False,
                    shipping_address=default_address,
                    cod_amount=cod_amount,
                    shipping_fee=shipping_fee
                )
            request.session['bundle_order'] = order.order_id
            print(f"Order ID {order.order_id} saved to session.")
            return JsonResponse({'message': 'Order created successfully', 'order_id': order.order_id}, status=200)
        else:
            print("User is not authenticated. Creating temporary user.")
            referrer = request.session.get('funnel_referrer')
            if not referrer:
                return JsonResponse({'error': 'Referrer not found in session'}, status=400)
            referrer_user = get_object_or_404(User, username=referrer)
            print(f'Referrer: {referrer}, Order Item Quantity: {total_quantity}')

            shipping_fee = sf_calculator(region=region, qty=total_quantity)
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
            temporary_username = first_name.lower()[0] + last_name.lower() + random_suffix
            temporary_password = User.objects.make_random_password(length=6)

            temporary_user, user_created = User.objects.get_or_create(
                username=temporary_username,
                defaults={
                    'password': temporary_password,
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'referred_by': referrer_user,
                }
            )
            print(f"Temporary user created: {temporary_username}, User created: {user_created}")

            shipping_address, created = Address.objects.get_or_create(
                user=temporary_user,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'phone': phone,
                    'line1': line1,
                    'barangay': barangay,
                    'city': city,
                    'province': province,
                    'region': region,
                    'postcode': postcode,
                    'message': message,
                }
            )
            print(f"Shipping address created for temporary user: {temporary_username}, Address created: {created}")

            order = Order.objects.create(
                user=temporary_user,
                shipping_address=shipping_address,
                cod_amount=cod_amount,
                shipping_fee=shipping_fee,
                complete=False
            )
            print(f'Order ID: {order.order_id} created for temporary user.')
            request.session['bundle_order'] = order.order_id

            request.session['guest_user_data'] = {
                'username': temporary_username,
                'password': temporary_password,
                'email': temporary_user.email,
            }

            user = authenticate(request, username=temporary_username, password=temporary_password)

            # if guest user is authenticated send email for temporary account
            if user:
                send_temporary_account_email(user, first_name, temporary_username, temporary_password)

            return JsonResponse({'message': 'Order created successfully', 'order_id': order.order_id}, status=200)

    except User.DoesNotExist:
        return JsonResponse({'error': 'Referrer user not found'}, status=400)

    except Exception as e:
        print(f"Exception in create_order: {e}")
        return JsonResponse({'error': 'Internal Server Error'}, status=500)



class BecomeSellerView(TemplateView):
    title = "BecomeSeller"
    template_name = 'become-seller.html'
    context = {'title': title}

    def get_context_data(self, **kwargs):
        return self.context


class ComingSoonView(TemplateView):
    title = "ComingSoon"
    template_name = 'coming-soon.html'
    context = {'title': title}

    def get_context_data(self, **kwargs):
        return self.context


class Handle404View(View):
    title = "404"

    def get(self, request):
        context = self.get_context_data()
        return HttpResponseNotFound(render(request, '404.html', context=context))

    def get_context_data(self):
        return {'title': self.title}
