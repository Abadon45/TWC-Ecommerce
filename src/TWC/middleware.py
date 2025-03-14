import requests
import os

from django.http import Http404, HttpResponseRedirect
from django.http import HttpResponsePermanentRedirect
from django.conf import settings
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

import logging

from cart.utils import fetch_username, get_main_domain

logger = logging.getLogger(__name__)

def some_view(request):
    logger.debug(f"Session: {request.session.items()}")


class SubdomainMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """Process the subdomain and check username if needed."""
        # Extract the full host
        full_host = request.get_host()
        host_parts = full_host.split(".")

        # Determine if there is a subdomain
        request.subdomain = host_parts[0] if len(host_parts) > 2 else None

        # 🚨 Skip username checking for specific subdomains
        if request.subdomain in ["www", "admin"]:
            print("✅ Skipping subdomain checks for:", request.subdomain)
            return self.get_response(request)

        # If subdomain is "dashboard", handle login and username check
        if request.subdomain == "dashboard":
            sponsor = request.session.get("sponsor")
            request.session["referrer"] = sponsor if sponsor else None
            user = request.user
            username = user.username if user.is_authenticated else request.session.get("username", "")


            # Allow access to the login page without redirecting
            if request.path.startswith("/login/"):
                print("✅ User is on login page. Allowing access.")
                return self.get_response(request)  # Fixed the reference here

            if username:
                self.fetch_username(request, username)
            else:
                print("⚠️ No username found in session. Redirecting to dashboard login page.")
                self.debug_session(request)
                return HttpResponseRedirect(f"http://dashboard.{get_main_domain(request)}/login/")

        # Otherwise, check the username from the API
        elif request.subdomain:
            response = self.check_username(request, request.subdomain)
            if response:
                return response  # Return early if an error occurs

        # Continue processing the request
        return self.get_response(request)

    def fetch_username(self, request, username):
        """Fetch username from the API and store relevant session data."""
        if not username:
            print("⚠️ Username not found in session.")
            return

        api_url = settings.CHECK_USERNAME_API_URL.format(username=username)

        try:
            api_response = requests.get(api_url)
            api_response.raise_for_status()  # Raise an exception for HTTP errors

            data = api_response.json()
            is_success = data.get("success", False)

            if is_success:
                # Update session only if necessary
                request.session.update({
                    "messenger_link": data.get("messenger_link", request.session.get("messenger_link")),
                    "sponsor_mobile": data.get("mobile", request.session.get("mobile")),
                    "sponsor_fb_pixel": data.get("selling_pixel", request.session.get("sponsor_fb_pixel")),
                    "selling_capi_token": data.get("selling_capi_token", request.session.get("selling_capi_token")),
                    "first_name": data.get("first_name", request.session.get("first_name")),
                    "middle_name": data.get("middle_name", request.session.get("middle_name")),
                    "last_name": data.get("last_name", request.session.get("last_name")),
                    "image": data.get("image", request.session.get("image")),
                    "is_seller": data.get("is_seller", request.session.get("is_seller")),
                    "is_member": data.get("is_member", request.session.get("is_member")),
                    "email": data.get("email", request.session.get("email")),
                    "sponsor_username": data.get("sponsor", request.session.get("sponsor_username")),
                })

                # ✅ Ensure session is properly saved
                request.session.modified = True
                request.session.save()

                sponsor = request.session.get("sponsor_username")
                is_member = request.session.get("is_member")

                return None
            else:
                print(f"❌ Username check failed for: {username}")
                raise Http404(f'User "{username}" Does Not Exist.')

        except requests.RequestException as e:
            print(f"🚨 API request failed: {e}")
            raise Http404("Server Is Under Maintenance.")

    def check_username(self, request, username):
        """Check username validity from the API and store session data."""
        if username in ["www", "admin"]:
            return None  # Ignore checking for these subdomains

        return self.fetch_username(request, username)

    def debug_session(self, request):
        """Print the session data before redirecting."""
        print(f"🔎 SESSION DEBUG: {dict(request.session)}")


class RedirectToWWW:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()

        # Ensure we only redirect if "www." is missing
        if not host.startswith("www.") and host in ["twconline.store", "twcstoredevtest.com", "devtest.store"]:
            new_url = request.build_absolute_uri().replace(f"{host}", f"www.{host}")
            return HttpResponsePermanentRedirect(new_url)

        # If already www., proceed normally
        return self.get_response(request)


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