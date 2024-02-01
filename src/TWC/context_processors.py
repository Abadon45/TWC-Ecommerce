# TWC/context_processors.py
from django.conf import settings

def main_site_url(request):
    return {'MAIN_SITE_URL': settings.MAIN_SITE_URL}

def site_urls(request):
    return {
        'MAIN_SITE_URL': settings.MAIN_SITE_URL,
        'DASHBOARD_URL': settings.DASHBOARD_URL,
        'ADMIN_URL': settings.ADMIN_URL,
    }