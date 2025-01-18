from decimal import Decimal

from django.views.generic import View, TemplateView
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound
from django.contrib.auth import get_user_model
from django.utils.text import capfirst
from django.urls import reverse
from django.db import transaction
from cart.utils import generate_invoice_number, get_client_ip, get_client_user_agent, conversion_api
from onlinestore.models import SiteSetting
from onlinestore.utils import fetch_vw_inventory
from django.templatetags.static import static

from facebook_business.adobjects.serverside.custom_data import CustomData
from facebook_business.adobjects.serverside.user_data import UserData


import random
import requests
import json

User = get_user_model()


class IndexView(TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):

        base_api_url = 'https://dashboard.twcako.com/shop/api/get-product/'

        endpoints = {
            'is_trending': f"{base_api_url}?is_trending=true",
            'is_popular': f"{base_api_url}?is_popular=true",
            'new_arrival': f"{base_api_url}?new_arrival=true",
        }

        # Fetch each filtered list from the API
        products_data = {}
        for key, url in endpoints.items():
            try:
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                products_data[key] = data.get("products", []) if data.get("success") else []
            except requests.exceptions.RequestException as e:
                products_data[key] = []  # Fallback to empty list in case of API error

        # Fetch the main products list (e.g., without "twc" in `category_1`)
        try:
            response = requests.get(base_api_url)
            response.raise_for_status()
            data = response.json()
            products = data.get("products", []) if data.get("success") else []
            products = [product for product in products if product.get('category_1') != 'twc']
        except requests.exceptions.RequestException as e:
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

        subcategories_choices = [
            ('sante-nutraceutical', 'Health & Wellness'),
            ('sante-beverage', 'Healthy Beverages'),
            ('sante-intimate_care', 'Intimate Care'),
            ('bath-body', 'Bath & Body'),
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
            'title': "Home",
            'username': guest_user_info.get('username'),
            'password': guest_user_info.get('password'),
            'email': guest_user_info.get('email'),
            'new_guest_user': new_guest_user,
            'has_existing_order': request.session.get('has_existing_order', False),
            'products': products,
            'is_trending': products_data['is_trending'],
            'is_popular': products_data['is_popular'],
            'new_arrival': products_data['new_arrival'],
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


class ProductFunnelView(View):
    title = "Product Funnel"

    def get(self, request, *args, **kwargs):
        product = kwargs.get('product', None)

        inventory = fetch_vw_inventory(request)

        # Check the quantities of specific products
        if 'pf-vw' in request.path:
            quantity_dict = inventory.get('quantity_dict', {})
            section = 'vw'
            if product == ['weight-loss', 'old-age'] and quantity_dict.get('fusion_coffee', 0) == 0:
                return redirect(f'/pf-ds/{product}/')
            elif product == 'boost-coffee' and quantity_dict.get('boost_coffee', 0) == 0:
                return redirect(f'/pf-ds/{product}/')
            elif product in ['barley-for-cancer', 'barley-for-diabetes', 'barley-for-high-blood'] and quantity_dict.get(
                    'barley_powder_10', 0) == 0:
                return redirect(f'/pf-ds/{product}/')
        elif 'pf-ds' in request.path:
            section = 'ds'
        else:
            raise Http404("Invalid URL pattern")

        product_name = ''
        content_ids = []

        # Ensure 'unique_id' exists in the session or generate a new one
        unique_id = request.session.get('unique_id', generate_invoice_number())
        if 'unique_id' not in request.session:
            request.session['unique_id'] = unique_id

        # Create the event ID based on the unique_id
        event_id = f'landing-page_{unique_id}'

        if product == 'barley-for-cancer':
            template_name = 'funnels/products/barley/cancer.html'
            product_name = 'Barley Juice For Cancer'
            content_ids = ['SPHN09415', 'TP009', 'TP378']
        elif product == 'barley-for-diabetes':
            template_name = 'funnels/products/barley/diabetes.html'
            product_name = 'Barley Juice For Diabetes'
            content_ids = ['SPHN09415', 'TP009', 'TP378']
        elif product == 'barley-for-high-blood':
            template_name = 'funnels/products/barley/high-blood.html'
            product_name = 'Barley Juice For Highblood'
            content_ids = ['SPHN09415', 'TP009', 'TP378']
        elif product == 'old-age':
            template_name = 'funnels/products/fusion-coffee/old-age.html'
            product_name = 'Fusion For Old Age'
            content_ids = ['SN0910', 'TP009', 'TP378']
        elif product == 'weight-loss':
            template_name = 'funnels/products/fusion-coffee/weight-loss.html'
            product_name = 'Fusion For Weightloss'
            content_ids = ['SN0910', 'TP009', 'TP378']
        elif product == 'boost-coffee':
            template_name = 'funnels/products/boost_coffee/index.html'
            product_name = 'Boost Coffee'
            content_ids = ['SB0204', 'TP009', 'TP378']
        else:
            raise Http404("Product is not available")


        request.session['event_name'] = product_name

        selling_capi_token = request.session.get('selling_capi_token', None)
        sponsor_fb_pixel = request.session.get('sponsor_fb_pixel', None)

        if selling_capi_token and sponsor_fb_pixel:
            # FUNNEL INTEGRATIONS
            external_id = unique_id
            fbp = request.COOKIES.get('_fbp')
            fbc = request.COOKIES.get('_fbc')

            try:
                client_ip_address = get_client_ip(request)
                client_user_agent = get_client_user_agent(request)
                capi_token = selling_capi_token
                first_name = request.GET.get('fn', '')
                last_name = request.GET.get('ln', '')
                mobile = request.GET.get('mobile', '')

                user_data = UserData(
                    first_name=first_name,
                    last_name=last_name,
                    phone=mobile if mobile else "",
                    external_id=external_id,
                    client_ip_address=client_ip_address,
                    client_user_agent=client_user_agent,
                    fbp=fbp,
                    fbc=fbc
                )

                custom_data = CustomData(
                    content_name=product_name,
                )

                conversion_api(
                    request,
                    access_token=capi_token,
                    pixel_id=sponsor_fb_pixel,
                    event_name=product_name,
                    event_id=event_id,
                    user_data=user_data,
                    custom_data=custom_data
                )
            except:
                pass
        context = {
            'title': self.title,
            'product': product,
            'section': section,
            'product_name': product_name,
            'content_ids': content_ids,
            'event_id': event_id,
        }

        # Render the template with the context
        return render(request, template_name, context)


@transaction.atomic
def create_order(request):
    shipping_fee = SiteSetting.get_fixed_shipping_fee()

    # Clear the previous cart and orders
    if 'ordered_items_by_shop' in request.session:
        request.session.pop('cart', None)
        request.session.pop('ordered_items_by_shop', None)

    try:
        # Use request.GET instead of request.POST
        product_details_str = request.GET.get("bundleDetails", '{}')

        try:
            product_details = json.loads(product_details_str)
        except json.JSONDecodeError:
            print("Error decoding JSON for product_details")
            product_details = {}

        # Convert to Decimal
        cod_amount = Decimal(request.GET.get("bundle_price", "0"))
        total_quantity = Decimal(request.GET.get("bundle_qty", "0"))

        promo = request.GET.get("promo", "")
        print(f'Promo: {promo}')

        print(f'Product details: {product_details}')

        items = []
        total_amount = Decimal(0)


        # Process each product in the order
        for product_detail in product_details.get('products', []):
            product_slug = product_detail['slug']

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

        if items:  # Ensure the 'items' list is not empty
            product_name = items[0]['product']['name']

            # Modify the product name based on keywords
            if 'Barley Powder' in product_name:
                product_name = f"Barley Powder {promo}"
            elif "Fusion Coffee" in product_name:
                product_name = f"Fusion Coffee {promo}"
            elif "Boost Coffee" in product_name:
                product_name = f"Boost Coffee {promo}"

            # Update the name in the first product
            items[0]['product']['name'] = product_name
            product_name_format = product_name.lower().replace(' ', '-')
            image = static(f'funnel/products/img/thank_you_page/{product_name_format}.webp')
            items[0]['product']['image'] = image

        # Append the items to the session data
        ordered_items_by_shop['promo']['items'] = items


        print(f"Order: {ordered_items_by_shop}")

        # Calculate the discount and ensure values are Decimal
        discount = total_amount + shipping_fee - cod_amount
        print(f'Discount: {discount}')

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

        print(f'Orders: {order_details}')  # Debugging: print out the order details

        request.session.modified = True

        return JsonResponse({
            'success': True,
            'redirect_url': reverse('cart:promo_checkout')
        })

    except Exception as e:
        print(f"Exception in create_order: {e}")
        return JsonResponse({'error': 'Internal Server Error'}, status=500)



class Handle404View(View):
    title = "404"

    def get(self, request, exception=None):
        context = self.get_context_data(exception=exception)
        return HttpResponseNotFound(render(request, '404.html', context=context))

    def get_context_data(self, exception=None):
        # Pass the exception message or a default one
        message = str(exception) if exception else "Oops... Page Not Found!"
        return {'title': self.title, 'message': message}
