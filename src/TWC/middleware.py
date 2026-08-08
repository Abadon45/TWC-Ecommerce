import requests
import os
import ipaddress

from django.http import Http404
from django.http import HttpResponsePermanentRedirect
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

import logging

logger = logging.getLogger(__name__)

def some_view(request):
    logger.debug(f"Session: {request.session.items()}")

from django.http import HttpResponsePermanentRedirect, Http404
import requests


class SubdomainMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        full_host = request.get_host()
        host_no_port = full_host.rsplit(':', 1)[0]
        print(f'Full Host: {full_host}')

        host_parts = host_no_port.split('.')

        if len(host_parts) > 2 and not self._is_local_host(host_no_port):
            request.subdomain = host_parts[0]
        else:
            request.subdomain = None

        print(f'Subdomain: {request.subdomain}')

        if request.subdomain:
            response = self.check_username(request, request.subdomain)
            if response:
                return response

        return self.get_response(request)

    def _is_local_host(self, hostname):
        if hostname in ['localhost', '127.0.0.1']:
            return True
        try:
            ipaddress.ip_address(hostname)
            return True
        except ValueError:
            return False

    def check_username(self, request, username):
        if username in ["www", "admin"]:
            return None

        # Skip redirect if URL already includes promo flags
        current_path = request.get_full_path()
        if "pf-vw" in current_path or "pf-ds" in current_path:
            print("🔁 Skipping redirect due to pf-vw or pf-ds in URL.")
            return None

        api_url = f'https://dashboard.twcako.com/account/api/check-username/{username}/'

        try:
            api_response = requests.get(api_url, verify=False, timeout=10)
            api_response.raise_for_status()

            data = api_response.json()
            is_success = data.get('success')
            messenger_link = data.get('messenger_link')
            sponsor_mobile = data.get('sponsor_mobile')
            sponsor_fb_pixel = data.get('selling_pixel')
            selling_capi_token = data.get('selling_capi_token')

            print(f'Data: {data}')

            if is_success:
                # Optional: keep session storage if still used anywhere
                request.session['referrer'] = username
                request.session['messenger_link'] = messenger_link
                request.session['sponsor_mobile'] = sponsor_mobile
                request.session['sponsor_fb_pixel'] = sponsor_fb_pixel
                request.session['selling_capi_token'] = selling_capi_token
                print(f"✅ Valid username: {username}. Redirecting...")

                full_path = request.get_full_path()
                if full_path.startswith('/shop'):
                    redirect_url = f"https://www.technowealthcreators.com/eshop?ref={username}"
                else:
                    redirect_url = f"https://www.technowealthcreators.com/?ref={username}"

                return HttpResponsePermanentRedirect(redirect_url)
            else:
                print(f'❌ Invalid username: {username}')
                raise Http404(f'User "{username}" Does Not Exist.')

        except requests.RequestException as e:
            print(f"❗ API request failed: {e}")
            raise Http404('Server Is Under Maintenance.')



class RedirectToWWW:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host_full = request.get_host()
        host = host_full.rsplit(':', 1)[0]

        host_parts = host.split('.')
        print(f'Host: {host_full}')
        print(f'HostParts: {host_parts}')

        if host in ['twconline.store', 'twcstoredevtest.com', 'devtest.store']:
            new_url = request.build_absolute_uri().replace(f"{host_full}", f"www.{host}")
            return HttpResponsePermanentRedirect(new_url)

        response = self.get_response(request)
        return response

class DynamicCSRFMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Extract the domain from the request
        domain = request.get_host().rsplit(':', 1)[0]
        if domain and domain not in settings.CSRF_TRUSTED_ORIGINS:
            # Add the domain to CSRF_TRUSTED_ORIGINS dynamically
            settings.CSRF_TRUSTED_ORIGINS.append(f'https://{domain}')


class CurrentDomainMiddleware(MiddlewareMixin):
    def process_request(self, request):
        host = request.get_host().rsplit(':', 1)[0]  # Get the host without the port
        domain_parts = host.split('.')

        # For localhost or numeric IPs, keep the full host instead of using last two parts
        if host == 'localhost' or self._is_ip_address(host):
            current_domain = host
        elif len(domain_parts) > 2:
            current_domain = '.'.join(domain_parts[-2:])  # Join the last two parts (domain + TLD)
        else:
            current_domain = host  # If no subdomain, use the whole host

        # Set the current domain in the request
        settings.CURRENT_DOMAIN = current_domain

    def _is_ip_address(self, host):
        try:
            ipaddress.ip_address(host)
            return True
        except ValueError:
            return False


class SubdomainSessionMiddleware(MiddlewareMixin):
    """Keep one session cookie name across the storefront hosts.

    SessionMiddleware has already loaded the session before this middleware
    runs. Mutating ``request.session.cookie_name`` here makes Django save a new
    cookie name that SessionMiddleware will not read on the next request.
    """

    def process_request(self, request):
        return None
