from django.http import Http404
from django.contrib.auth import get_user_model
from django.http import HttpResponsePermanentRedirect
from django_hosts import host
from user.models import User
import logging
import os

User = get_user_model()

logger = logging.getLogger(__name__)


class SubdomainMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Extract the full host
        full_host = request.get_host()

        # Split the host into parts (subdomain.domain.com -> ['subdomain', 'domain', 'com'])
        host_parts = full_host.split('.')

        # Check if the host has a subdomain (at least three parts)
        if len(host_parts) > 2:
            request.subdomain = host_parts[0]  # The first part is the subdomain
        else:
            request.subdomain = None  # Set subdomain to None if there is no subdomain

        # Custom logic based on subdomain
        if request.subdomain:
            try:
                # Try to get the user based on the subdomain
                request.user = User.objects.get(username=request.subdomain)
            except User.DoesNotExist:
                raise Http404("User does not exist")

        # Log the subdomain for debugging purposes
        logger.debug(f"Subdomain: {request.subdomain}")

        # Continue processing the request
        response = self.get_response(request)

        cookie_domain = None if os.getenv('ENV') == 'development' else '.twconline.store'

        # Set the session cookie with the correct domain
        response.set_cookie(
            'sessionid',
            request.session.session_key,
            domain=cookie_domain,
            httponly=True
        )

        return response

class RedirectToWWW:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        env = os.getenv('ENV', 'production')
        host = request.get_host()
        if env == 'production' and host == 'twconline.store':
            return HttpResponsePermanentRedirect(f'https://www.twconline.store{request.get_full_path()}')
        response = self.get_response(request)
        return response