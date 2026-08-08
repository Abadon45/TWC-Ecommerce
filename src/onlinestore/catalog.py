"""Local product catalog used by the customer-facing storefront.

The dashboard product endpoint is no longer required at runtime.  The JSON
snapshot is intentionally loaded lazily and cached for the lifetime of the
process so shop pages do not repeatedly read the file from disk.
"""

import copy
import json
from functools import lru_cache
from pathlib import Path

from django.conf import settings


CATALOG_PATH = Path(settings.BASE_DIR) / "onlinestore" / "data" / "products.json"


@lru_cache(maxsize=1)
def _catalog_payload():
    with CATALOG_PATH.open(encoding="utf-8") as catalog_file:
        payload = json.load(catalog_file)

    if not payload.get("success") or not isinstance(payload.get("products"), list):
        raise ValueError("The local product catalog has an invalid format.")
    return payload


def get_products():
    """Return a copy so view-level filtering never mutates the cached data."""
    return copy.deepcopy(_catalog_payload()["products"])


def get_product_by_slug(slug):
    return next((product for product in get_products() if product.get("slug") == slug), None)
