import os
import requests

from django.http import Http404, JsonResponse


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