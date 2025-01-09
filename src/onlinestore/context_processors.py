# ecommerce context_processors.py

from .models import SiteSetting
from django.conf import settings

import requests


def referrer(request):
    try:
        sponsor_messenger = request.session.get('messenger_link', None)
        # sponsor_mobile = request.session.get('mobile', None)
        sponsor = request.session.get('referrer', None)
        sponsor_fb_pixel = request.session.get('sponsor_fb_pixel', None)
        selling_capi_token = request.session.get('selling_capi_token', None)


        host = request.get_host().split(':')[0]  # Get the host without the port
        domain_parts = host.split('.')

        # Check if there's a subdomain (i.e., more than 2 parts)
        if len(domain_parts) > 2:
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
        # Get the cart data from session
        cart = request.session.get('cart', {})

        # Initialize variables
        cart_items = 0
        ordered_items = {}
        total_cart_subtotal = 0
        FIXED_SHIPPING_FEE = SiteSetting.get_fixed_shipping_fee()

        # Iterate through the cart items
        for slug, item in cart.items():
            product_slug = item.get('slug')
            quantity = item.get('quantity', 0)

            # Fetch product details from the API
            product_url = f'{settings.PRODUCT_URL_API}{product_slug}'
            response = requests.get(product_url)
            if response.status_code == 200:
                product_data = response.json().get('product', {})
                if product_data:
                    # Calculate item subtotal
                    item_subtotal = float(product_data.get('customer_price', 0)) * quantity
                    total_cart_subtotal += item_subtotal

                    print(f'Cart Total: {total_cart_subtotal}')

                    # Update ordered_items dictionary by category
                    category = product_data.get('category_1', 'other')
                    if category not in ordered_items:
                        ordered_items[category] = []

                    ordered_items[category].append({
                        'product': product_data,
                        'quantity': quantity,
                        'subtotal': item_subtotal
                    })

                    cart_items += quantity

            else:
                print(f"Error fetching product data for slug {product_slug}: HTTP {response.status_code}")


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
        response = requests.get(ph_numbers_api_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        prefixes = data.get('ph_number_prefixes', [])
    except requests.RequestException as e:
        # Log the error if necessary
        print(f"Error fetching PHNumberPrefixes: {e}")
        prefixes = []

    return {'ph_number_prefixes': prefixes}
