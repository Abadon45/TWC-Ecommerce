# ecommerce context_processors.py

from django.contrib.auth import get_user_model

import requests

User = get_user_model()


def referrer(request):
    try:
        sponsor_messenger = request.session['messenger_link']
        if sponsor_messenger:
            return {'referrer': sponsor_messenger}
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
        }

    except Exception as e:
        print(f"Error in cart_items view: {e}")
        return {'cart_items': 0}