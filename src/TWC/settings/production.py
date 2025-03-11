from .base import *
import os
from django.conf import settings
from dotenv import load_dotenv

load_dotenv()

DEBUG = False

# Default settings
PARENT_HOST = 'twconline.store'
SITE_DOMAIN = 'twconline.store'
SESSION_COOKIE_DOMAIN = 'twconline.store'
DOMAIN_NAME = 'twconline.store'
SESSION_COOKIE_SECURE = False

# Use the CURRENT_DOMAIN set in the middleware
current_domain = getattr(settings, 'CURRENT_DOMAIN', None)

if current_domain == 'twconline.store':
    # Production settings
    PARENT_HOST = 'twconline.store'
    SITE_DOMAIN = 'twconline.store'
    SESSION_COOKIE_DOMAIN = '.twconline.store'
    SESSION_COOKIE_SECURE = True
elif current_domain == 'twcstoredevtest.com':
    # Test server settings
    PARENT_HOST = 'twcstoredevtest.com'
    SITE_DOMAIN = 'twcstoredevtest.com'
    SESSION_COOKIE_DOMAIN = '.twcstoredevtest.com'
    DOMAIN_NAME = 'twcstoredevtest.com'
    SESSION_COOKIE_SECURE = False
else:
    SESSION_COOKIE_DOMAIN = None

SESSION_COOKIE_NAME = "twccookie"
SESSION_COOKIE_SAMESITE = "None" if SESSION_COOKIE_SECURE else "Lax"
CSRF_COOKIE_DOMAIN = SESSION_COOKIE_DOMAIN
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

# Allow cookies on HTTP for testing

SESSION_COOKIE_HTTPONLY = True
CORS_ORIGIN_ALLOW_ALL = True

DASHBOARD_URL = 'https://dashboard.twconline.store'
ADMIN_URL = 'https://admin.twconline.store'
MAIN_SITE_URL = 'https://www.twconline.store'

