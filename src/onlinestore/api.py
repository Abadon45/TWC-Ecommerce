import os
import requests

from django.http import Http404, JsonResponse

from TWC import settings


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
    url = settings.FETCH_ORDERS_API_URL.format(username=username)
    print(f"Fetching orders for user: {username}")
    print(f"API URL: {url}")

    try:
        response = requests.get(url)
        print(f"API Response Status Code: {response.status_code}")

        response.raise_for_status()  # Raises an error if the request failed
        data = response.json()  # Ensure we parse JSON
        print(f"Raw API Response Data: {data}")

        # Extract the 'orders' list correctly
        results = data.get("results", {})  # Ensure results is a dict
        orders = results.get("orders", [])  # Extract 'orders' inside 'results'

        print(f"Extracted Orders Data: {orders}")

        # Ensure orders is a list
        if not isinstance(orders, list):
            print("Warning: 'orders' is not a list. Defaulting to an empty list.")
            orders = []

        # Extract only the required fields
        filtered_orders = [
            {
                "order_number": order.get("order_number", ""),
                "timestamp": order.get("timestamp", ""),
                "cod_amount": float(order.get("cod_amount", 0)),  # Ensure float conversion
                "status": order.get("status", "").lower(),  # Convert status to lowercase
            }
            for order in orders
        ]

        print(f"Final Filtered Orders: {filtered_orders}")
        return {"orders": filtered_orders, "count": len(filtered_orders)}

    except requests.RequestException as e:
        print(f"Error fetching user orders: {e}")
        return {"orders": [], "count": 0}  # Default empty structure
