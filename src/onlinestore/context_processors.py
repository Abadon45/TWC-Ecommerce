# ecommerce context_processors.py

from .models import SiteSetting
from django.conf import settings

import ipaddress
import json
import requests


def referrer(request):
    try:
        sponsor_messenger = request.session.get('messenger_link', None)
        # sponsor_mobile = request.session.get('mobile', None)
        sponsor = request.session.get('referrer', None)
        sponsor_fb_pixel = request.session.get('sponsor_fb_pixel', None)
        selling_capi_token = request.session.get('selling_capi_token', None)


        host = request.get_host().rsplit(':', 1)[0]  # Get the host without the port
        domain_parts = host.split('.')

        def _is_ip_address(value):
            try:
                ipaddress.ip_address(value)
                return True
            except ValueError:
                return False

        if host == 'localhost' or _is_ip_address(host):
            current_domain = host
        elif len(domain_parts) > 2:
            current_domain = '.'.join(domain_parts[-2:])  # Join the last two parts (domain + TLD)
        else:
            current_domain = host  # If no subdomain, use the whole host

        print(f'Current domain: {current_domain}')

        dev_admin = ""
        dev_domain = ""

        valid_domain = {'devtest.store', 'twcstoredevtest.com'}

        if current_domain in valid_domain:
            dev_domain = current_domain

        valid_sponsors = {'noypangan', 'evgeronilla', 'avail', 'machero', 'jcerdina'}

        if sponsor in valid_sponsors:
            dev_admin = sponsor

        print(f'Sponsor FB Pixel: {sponsor_fb_pixel}')

        if sponsor_messenger or dev_admin:
            return {
                'referrer': sponsor_messenger,
                'dev_admin': dev_admin,
                'dev_domain': dev_domain,
                'sponsor_fb_pixel': sponsor_fb_pixel,
                'selling_capi_token': selling_capi_token,
            }
        return {'referrer': None}
    except Exception as e:
        print(f"Error in referrer context processor: {e}")
        return {'referrer': None}

def cart_items(request):
    try:
        cart = request.session.get('cart', {})
        raw_cookie_cart = request.COOKIES.get('userCart', '')
        if raw_cookie_cart:
            try:
                cookie_cart = json.loads(raw_cookie_cart)
                if isinstance(cookie_cart, dict):
                    cart = cookie_cart
            except (TypeError, ValueError):
                pass

        # Initialize variables
        cart_items = 0
        ordered_items = {}
        total_cart_subtotal = 0
        FIXED_SHIPPING_FEE = SiteSetting.get_fixed_shipping_fee()

        # Cart entries already contain display data captured when the item was
        # added. A temporary product API failure must not make a valid session
        # cart look empty in the header or drawer.
        for slug, item in cart.items():
            quantity = item.get('quantity', 0)
            if not isinstance(quantity, int) or quantity <= 0:
                continue

            price = float(item.get('price', 0) or 0)
            item_subtotal = price * quantity
            total_cart_subtotal += item_subtotal
            category = item.get('shop', 'other')
            product_data = {
                'id': item.get('id'),
                'sku': item.get('id'),
                'name': item.get('name', slug),
                'slug': item.get('slug', slug),
                'category_1': category,
                'image_1': item.get('image'),
                'customer_price': price,
                'price': price,
            }
            ordered_items.setdefault(category, []).append({
                'product': product_data,
                'quantity': quantity,
                'subtotal': item_subtotal,
            })
            cart_items += quantity


        return {
            'cart_items': cart_items,
            'order_products': ordered_items,
            'total_cart_subtotal': total_cart_subtotal,
            'FIXED_SHIPPING_FEE': FIXED_SHIPPING_FEE
        }

    except Exception as e:
        print(f"Error in cart_items view: {e}")
        return {'cart_items': 0}

def facebook_pixel_id(request):
    pixel_id = ""
    return {
        'pixel_id': pixel_id
    }


def ph_number_prefixes(request):
    """
    Fetch PHNumberPrefixes from the API and add them to the context.
    """
    ph_numbers_api_url = settings.PH_NUMBERS_PREFIXES_API
    try:
        response = requests.get(ph_numbers_api_url, verify=False, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        prefixes = data.get('ph_number_prefixes', [])
    except requests.RequestException as e:
        # Log the error if necessary
        print(f"Error fetching PHNumberPrefixes: {e}")
        prefixes = []

    return {'ph_number_prefixes': prefixes}
