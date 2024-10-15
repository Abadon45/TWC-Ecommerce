# ecommerce context_processors.py

from django.contrib.auth import get_user_model
from .models import SiteSetting

import requests

User = get_user_model()


def referrer(request):
    try:
        host = request.get_host().split(':')[0]  # Get the host without the port
        domain_parts = host.split('.')

        # Check if there's a subdomain (i.e., more than 2 parts)
        if len(domain_parts) > 2:
            current_domain = '.'.join(domain_parts[-2:])  # Join the last two parts (domain + TLD)
        else:
            current_domain = host  # If no subdomain, use the whole host

        valid_domain = {'devtest.store', 'twcstoredevtest.com'}

        if current_domain in valid_domain:
            request.session['dev_domain'] = current_domain

        print(f'Domain: {current_domain}')

        sponsor_messenger = request.session.get('messenger_link', None)
        sponsor = request.session.get('referrer', None)

        valid_sponsors = {'noypangan', 'evgeronilla', 'avail', 'machero', 'jcerdina'}

        if sponsor in valid_sponsors:
            request.session['admin'] = sponsor

        dev_admin = request.session.get('admin', None)
        dev_domain = request.session.get('dev_domain', None)
        print(f'Admin: {dev_admin}')
        if sponsor_messenger or dev_admin:
            return {
                'referrer': sponsor_messenger,
                'dev_admin': dev_admin,
                'dev_domain': dev_domain,
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
            product_url = f'https://dashboard.twcako.com/shop/api/get-product/?slug={product_slug}'
            response = requests.get(product_url, verify=False)
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