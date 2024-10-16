from decimal import Decimal

from django.views.generic import View, TemplateView
from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import render, redirect
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
from onlinestore.models import SiteSetting
from onlinestore.utils import is_valid_username, check_sponsor_and_redirect, send_temporary_account_email

import random
import string
import requests
import json

User = get_user_model()


class IndexView(TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):

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

        # Exclude products with category_1 = 'twc'
        products = [product for product in products if product.get('category_1') != 'twc']

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
            ('sante-nutraceutical', 'Health & Wellness'),
            ('sante-beverage', 'Healthy Beverages'),
            ('sante-intimate_care', 'Intimate Care'),
            ('bath-body', 'Bath & Body'),
            ('mood', 'Watches'),
            ('chingu', 'Bags'),
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
            raise Http404("Product is not available")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.kwargs.get('product')

        context.update({'product': product})

        return context


@transaction.atomic
def create_order(request):
    FIXED_SHIPPING_FEE = SiteSetting.get_fixed_shipping_fee()
    if 'ordered_items_by_shop' in request.session:
        request.session.pop('cart', None)
        request.session.pop('ordered_items_by_shop', None)

    try:
        # Retrieve customer and address details from POST data
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

        product_details_str = request.POST.get("bundleDetails", '{}')

        try:
            product_details = json.loads(product_details_str)
        except json.JSONDecodeError:
            print("Error decoding JSON for product_details")
            product_details = {}

        cod_amount = Decimal(request.POST.get("bundle_price", "0"))  # Convert to Decimal
        total_quantity = Decimal(request.POST.get("bundle_qty", "0"))  # Convert to Decimal

        # Save shipping address in session
        request.session['shipping_address'] = {
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
            'line1': line1,
            'region': region,
            'province': province,
            'city': city,
            'barangay': barangay,
            'postcode': postcode,
            'message': message,
        }

        # Calculate the shipping fee
        if FIXED_SHIPPING_FEE > 0:
            shipping_fee = Decimal(FIXED_SHIPPING_FEE)  # Convert to Decimal
        else:
            qty = total_quantity
            shipping_fee = Decimal(sf_calculator(region=region, qty=qty))

        print(f'Product details: {product_details}')

        items = []
        total_amount = Decimal(0)

        # Process each product in the order
        for product_detail in product_details.get('products', []):
            product_slug = product_detail['slug']
            print(f'Product slug: {product_slug}')

            product_url = f'https://dashboard.twcako.com/shop/api/get-product/?slug={product_slug}'
            try:
                response = requests.get(product_url)
                response.raise_for_status()
                product_data = response.json()

                if product_data['success']:
                    product = product_data['product']
                    get_total = product_detail['quantity'] * Decimal(product['customer_price'])
                    total_amount += get_total
                    print(f'Total amount: {total_amount}')
                    item = {
                        'product': {
                            'id': product['sku'],
                            'name': product['name'],
                            'shop': 'promo',
                            'slug': product_slug,
                            'image': product.get('image_1', None),
                            'price': product['customer_price'],
                        },
                        'quantity': product_detail['quantity'],
                        'get_total': f'{get_total:.2f}',
                    }
                    items.append(item)
                else:
                    print("Failed to fetch the product")

            except requests.RequestException as e:
                print(f"Error fetching product data: {e}")

        print(f'Items: {items}')

        # Retrieve bundle order data from session (provided by sales funnel jQuery)
        ordered_items_by_shop = request.session.get('ordered_items_by_shop', {})

        if 'promo' not in ordered_items_by_shop:
            ordered_items_by_shop['promo'] = {'items': []}

        # Calculate the discount and ensure values are Decimal
        discount = total_amount + shipping_fee - cod_amount

        order_details = {
            'promo': {
                'items': items,
                'total_quantity': str(total_quantity),
                'subtotal': str(total_amount),
                'shipping_fee': str(shipping_fee),
                'discount': str(discount),
                'cod_amount': str(cod_amount),
            }
        }
        request.session['ordered_items_by_shop'] = order_details

        request.session.modified = True

        return JsonResponse({
            'success': True,
            'redirect_url': reverse('cart:promo_checkout')
        })

    except Exception as e:
        print(f"Exception in create_order: {e}")
        return JsonResponse({'error': 'Internal Server Error'}, status=500)

def create_xendit_invoice(request):
    # Xendit API URL for creating an invoice
    xendit_url = "https://api.xendit.co/v2/invoices"

    # Assuming you have the following data from your session or request
    customer_name = "Emmanuel Pangan"  # Replace with actual customer name
    customer_email = "noypangan5@gmail.com"  # Replace with actual customer email
    customer_phone = "+639177700256"  # Replace with actual customer phone number

    # Assuming you have a list of items from the shopping cart
    items = [
        {
            "name": "DW Men's Single Gold Watch",
            "quantity": 1,
            "price": float(1249)
        },
        {
            "name": "Natureal Toothpaste 100ml with Brosse Toothbrush",
            "quantity": 2,
            "price": float(960)
        }
    ]

    # Get shipping amount and convert to float if it's a Decimal
    shipping_amount = float(SiteSetting.get_fixed_shipping_fee())

    # Calculate total amount from items
    total_amount = sum(item["quantity"] * item["price"] for item in items) + shipping_amount

    # Create invoice items for the payload
    invoice_items = [
        {
            "name": item["name"],
            "quantity": item["quantity"],
            "price": item["price"]
        }
        for item in items
    ]

    # Add shipping cost as a separate item
    invoice_items.append({
        "name": "Shipping Cost",
        "quantity": 1,  # Show quantity as 1 for the shipping item
        "price": shipping_amount,  # Shipping amount
        "description": "Flat rate shipping fee"
    })

    # Invoice data that will be sent to Xendit API
    payload = {
        "external_id": "your_unique_invoice_id",  # Replace with your unique invoice ID
        "payer_email": customer_email,             # Customer email
        "description": "TWC Online Store Payment",  # Description of the payment
        "amount": total_amount,                     # Total amount in IDR
        "success_redirect_url": "http://noypangan.devtest.store:8000/cart/checkout/complete/",
        "items": invoice_items,                     # List of items in the invoice
        "payer_names": customer_name,                # Customer name
        "phone_number": customer_phone               # Customer phone number
    }

    # Xendit API key from settings
    api_key = settings.XENDIT_API_KEY

    try:
        # Send the POST request to Xendit API
        response = requests.post(
            xendit_url,
            json=payload,
            auth=(api_key, '')  # Xendit API uses basic auth with just the API key and empty password
        )

        # Check if the request was successful
        if response.status_code == 200:
            invoice_data = response.json()
            invoice_url = invoice_data['invoice_url']
            print(f'Redirecting to Xendit Invoice URL: {invoice_url}')  # Debugging log

            return redirect(invoice_url)
        else:
            print(f'Error response from Xendit: {response.json()}')  # Debugging log
            return JsonResponse({"status": "error", "message": response.json()}, status=response.status_code)

    except requests.exceptions.RequestException as e:
        print(f'Exception occurred: {str(e)}')  # Debugging log
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


class BecomeSellerView(TemplateView):
    title = "BecomeSeller"
    template_name = 'become-seller.html'
    context = {'title': title}

    def get_context_data(self, **kwargs):
        return self.context


class Handle404View(View):
    title = "404"

    def get(self, request, exception=None):
        context = self.get_context_data(exception=exception)
        return HttpResponseNotFound(render(request, '404.html', context=context))

    def get_context_data(self, exception=None):
        # Pass the exception message or a default one
        message = str(exception) if exception else "Oops... Page Not Found!"
        return {'title': self.title, 'message': message}
