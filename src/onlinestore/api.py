import os
import requests

from django.http import Http404, JsonResponse

from TWC import settings
from cart.utils import fetch_product_from_slug


def fetch_quantity_api(slug):
    HOST_DOMAIN = os.environ.get("HOST_DOMAIN", "twcako")
    product_detail_url = f'https://dashboard.{HOST_DOMAIN}.com/shop/api/get-product/?slug={slug}'
    try:
        response = requests.get(product_detail_url, verify=False)
        response.raise_for_status()
        product_data = response.json()

        # Check if the product exists
        product = product_data.get('product')
        if not product:
            raise Http404("Product not found.")

        # Get the stock quantity
        quantity = product.get('quantity', 0)
        category = product.get('category_1', "")

        excluded_category = ['promos', 'sante', 'twc']
        supplier_product = False

        if category not in excluded_category:
            supplier_product = True

        return quantity, supplier_product

    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        return JsonResponse({'error': 'Unable to fetch product details from the server.'}, status=500)

    except requests.exceptions.RequestException as req_err:
        print(f'Request error occurred: {req_err}')
        return JsonResponse({'error': 'Request to product API failed.'}, status=500)


def fetch_user_orders(username):
    """
    Fetch user orders from the API and enrich them with product details.
    """
    url = settings.FETCH_ORDERS_API_URL.format(username=username)

    try:
        response = requests.get(url, timeout=10)  # 10-second timeout

        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        data = response.json()

        # Ensure the response structure contains 'results'
        results = data.get("results", {})
        if not isinstance(results, dict):
            results = {}

        # Extract 'orders' safely
        orders = results.get("orders", [])
        if not isinstance(orders, list):
            orders = []

        # Process orders
        filtered_orders = []
        for order in orders:
            order_number = order.get("order_number", "")
            timestamp = order.get("timestamp", "")
            cod_amount = float(order.get("cod_amount", 0))  # Ensure float conversion
            status = order.get("status", "").lower()  # Convert to lowercase

            # Ensure 'items' is a list of dictionaries
            item_slugs = order.get("items", [])
            if not isinstance(item_slugs, list):
                item_slugs = []

            # Fetch product details for each item
            products = []
            for item in item_slugs:
                if isinstance(item, dict):  # Ensure item is a dictionary
                    product_slug = item.get("product__slug") or item.get("product_db__slug")  # Get the slug directly
                    product_qty = item.get("total_qty", 0)

                    if product_slug:  # Only fetch if slug is valid
                        try:
                            product_data = fetch_product_from_slug(product_slug)
                            product_data["quantity"] = product_qty
                            products.append(product_data)
                        except Exception as e:
                            print(f"Error fetching product {product_slug}: {e}")

            address = order.get("customer_profile", [])

            filtered_orders.append({
                "order_number": order_number,
                "timestamp": timestamp,
                "cod_amount": cod_amount,
                "status": status,
                "products": products,
                "address": address
            })

        return {"orders": filtered_orders, "count": len(filtered_orders)}

    except requests.Timeout:
        print("[FETCH] Error: API request timed out.")
    except requests.RequestException as e:
        print(f"[FETCH] Error fetching user orders: {e}")
    except ValueError:
        print("[FETCH] Error: Failed to decode JSON response.")

    return {"orders": [], "count": 0}
