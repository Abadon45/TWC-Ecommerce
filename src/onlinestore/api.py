from django.http import Http404
from onlinestore.catalog import get_product_by_slug


def fetch_quantity_api(slug):
    product = get_product_by_slug(slug)
    if not product:
        raise Http404("Product not found.")

    quantity = int(product.get('quantity', 0) or 0)
    supplier_product = product.get('category_1', '') not in ['promos', 'sante', 'twc']
    return quantity, supplier_product
