import requests
import os

from django.http import Http404, HttpResponseRedirect
from django.contrib.auth import get_user_model
from django.http import HttpResponsePermanentRedirect
from django.urls import reverse
from django_hosts import host
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse


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
        print(f'Checking username: {username} via API: {api_url}')

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
                return
            else:
                print(f'Username check failed for: {username}')  # Debugging
                return self.redirect_to_www(request)

        except requests.RequestException as e:
            print(f"API request failed: {e}")  # Debugging
            print(reverse('handle_404'))
            return self.redirect_to_www(request)

    def redirect_to_www(self, request):
        # Extract the current domain without the subdomain
        host_parts = request.get_host().split('.')
        domain = '.'.join(host_parts[1:])  # Skip the subdomain part
        new_url = f'http://www.{domain}{reverse("handle_404")}'
        print(f"Redirecting to: {new_url}")
        return HttpResponseRedirect(new_url)


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
