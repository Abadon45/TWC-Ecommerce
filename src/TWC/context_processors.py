# TWC/context_processors.py
import requests
from django.conf import settings
from django.http import JsonResponse

from onlinestore.api import online_store_settings


def main_site_url(request):
    return {'MAIN_SITE_URL': settings.MAIN_SITE_URL}

def site_urls(request):
    print(settings.DASHBOARD_URL)
    return {
        'MAIN_SITE_URL': settings.MAIN_SITE_URL,
        'DASHBOARD_URL': settings.DASHBOARD_URL,
        'ADMIN_URL': settings.ADMIN_URL,
    }



