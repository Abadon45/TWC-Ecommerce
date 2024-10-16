from django.conf import settings

from .base import *

DEBUG = False

# Default settings
PARENT_HOST = 'twconline.store'
SITE_DOMAIN = 'twconline.store'
SESSION_COOKIE_DOMAIN = 'twconline.store'
DOMAIN_NAME = 'twconline.store'

# Use the CURRENT_DOMAIN set in the middleware
current_domain = getattr(settings, 'CURRENT_DOMAIN', None)

if current_domain == 'twconline.store':
    # Production settings
    PARENT_HOST = 'twconline.store'
    SITE_DOMAIN = 'twconline.store'
    SESSION_COOKIE_DOMAIN = 'twconline.store'
elif current_domain == 'twcstoredevtest.com':
    # Test server settings
    PARENT_HOST = 'twcstoredevtest.com'
    SITE_DOMAIN = 'twcstoredevtest.com'
    SESSION_COOKIE_DOMAIN = 'twcstoredevtest.com'
    DOMAIN_NAME = 'twcstoredevtest.com'
else:
    SESSION_COOKIE_DOMAIN = None

# PARENT_HOST = 'twconline.store'
# SITE_DOMAIN = 'twconline.store'
# SESSION_COOKIE_DOMAIN = 'twconline.store'
# DOMAIN_NAME = 'twconline.store'

SESSION_COOKIE_NAME = "twccookie"
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_DOMAIN = SESSION_COOKIE_DOMAIN

CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = [
    "*.twconline.store",
    "*.twcstoredevtest.com",
]

REQUEST_API = 'https://dashboard.twcako.com/order/api/token/refresh/'
ORDER_API = 'https://dashboard.twcako.com/order/api/create-order/'

DASHBOARD_URL = 'https://dashboard.twconline.store'
ADMIN_URL = 'https://admin.twconline.store'
MAIN_SITE_URL = 'https://www.twconline.store'
