import requests
import os

from django.http import Http404
from django.http import HttpResponsePermanentRedirect
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

import logging

logger = logging.getLogger(__name__)

def some_view(request):
    logger.debug(f"Session: {request.session.items()}")

class SubdomainMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Extract the full host
        full_host = request.get_host()
        print(f'Full Host: {full_host}')

        # Split the host into parts
        host_parts = full_host.split('.')

        # Check if the host has a subdomain (at least three parts)
        if len(host_parts) > 2:
            request.subdomain = host_parts[0]  # The first part is the subdomain
        else:
            request.subdomain = None  # No subdomain

        print(f'Subdomain: {request.subdomain}')

        # If there's a subdomain, check it against the external API
        if request.subdomain:
            response = self.check_username(request, request.subdomain)
            if response:
                return response

        # Continue processing the request
        return self.get_response(request)

    def check_username(self, request, username):

        if username == "www":
            return None

        api_url = f'https://dashboard.twcako.com/account/api/check-username/{username}/'

        try:
            api_response = requests.get(api_url)
            api_response.raise_for_status()  # Raise an exception for HTTP errors

            data = api_response.json()
            is_success = data.get('success')
            messenger_link = data.get('messenger_link')

            if is_success:
                request.session['referrer'] = username
                request.session['messenger_link'] = messenger_link
                print(f"Referrer set: {username}, Messenger Link: {messenger_link}")
                return None
            else:
                print(f'Username check failed for: {username}')  # Debugging
                raise Http404(f'User "{username}" Does Not Exist.')

        except requests.RequestException as e:
            print(f"API request failed: {e}")  # Debugging
            raise Http404('User Does Not Exist.')


class RedirectToWWW:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        env = os.getenv('ENV', 'production')
        host = request.get_host()

        host_parts = host.split('.')

        if env == 'production' and len(host_parts) == 2 and host == 'twconline.store':
            return HttpResponsePermanentRedirect(f'https://www.twconline.store{request.get_full_path()}')

        response = self.get_response(request)
        return response

class DynamicCSRFMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Extract the domain from the request
        domain = request.get_host().split(':')[0]
        if domain and domain not in settings.CSRF_TRUSTED_ORIGINS:
            # Add the domain to CSRF_TRUSTED_ORIGINS dynamically
            settings.CSRF_TRUSTED_ORIGINS.append(f'https://{domain}')


class CurrentDomainMiddleware(MiddlewareMixin):
    def process_request(self, request):
        host = request.get_host().split(':')[0]  # Get the host without the port
        domain_parts = host.split('.')

        # Check if there's a subdomain
        if len(domain_parts) > 2:
            current_domain = '.'.join(domain_parts[-2:])  # Join the last two parts (domain + TLD)
        else:
            current_domain = host  # If no subdomain, use the whole host

        # Set the current domain in the request
        settings.CURRENT_DOMAIN = current_domain


class SubdomainSessionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Extract the host and subdomain
        host = request.get_host().split('.')
        if len(host) > 2:
            subdomain = host[0]  # Get the subdomain (e.g., subdomain.twconline.store)
            # Set a unique session cookie name for each subdomain
            request.session.cookie_name = f"session_{subdomain}"
        else:
            # Use a default session cookie name for the main domain
            request.session.cookie_name = "session_main"
