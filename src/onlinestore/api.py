import requests

from django.conf import settings
from django.http import Http404


def fetch_quantity_api(slug):
    product_detail_url = f"{settings.PRODUCT_URL_API}{slug}"
    try:
        response = requests.get(product_detail_url, verify=False, timeout=10)
        response.raise_for_status()
        product_data = response.json()

        if not isinstance(product_data, dict):
            raise ValueError('Invalid product API response format')

        # Check if the product exists
        product = product_data.get('product')
        if not product:
            raise Http404("Product not found.")

        # Get the stock quantity
        quantity = int(product.get('quantity', 0))
        category = product.get('category_1', "")

        excluded_category = ['promos', 'sante', 'twc']
        supplier_product = category not in excluded_category

        return quantity, supplier_product

    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred when fetching quantity for {slug}: {http_err}')
        raise Http404('Unable to fetch product details from the server.')

    except requests.exceptions.RequestException as req_err:
        print(f'Request error occurred when fetching quantity for {slug}: {req_err}')
        raise Http404('Request to product API failed.')

    except ValueError as value_err:
        print(f'Value error parsing quantity response for {slug}: {value_err}')
        raise Http404('Invalid response from product API.')
