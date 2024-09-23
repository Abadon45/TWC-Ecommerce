from TWC.settings.base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'admin.twconline.store']

SESSION_COOKIE_DOMAIN = None
CSRF_COOKIE_DOMAIN = None
DASHBOARD_URL = 'http://dashboard.twconline.store:8000'
ADMIN_URL = 'http://admin.twconline.store:8000'
MAIN_SITE_URL = 'http://localhost:8000'
