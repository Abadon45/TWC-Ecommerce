from django.http import Http404
from django.contrib.auth import get_user_model
from django_hosts import host
from billing.models import Customer

class SubdomainMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host_patterns = [
            host(r'www', 'TWC.urls', name='www'),
            host(r'admin', 'TWC.urls.admin', name='admin'),
            host(r'dashboard', 'TWC.urls.dashboard', name='dashboard'),
            host(r'(\w+)', 'TWC.urls', name='wildcard'),
        ]
        # Use django-hosts to set the subdomain attribute
        for pattern in host_patterns:
            match = pattern.compiled_regex.match(request.get_host())
            if match:
                try:
                    request.subdomain = match.group('subdomain')
                except IndexError:
                    request.subdomain = None
                break


        # Custom logic based on subdomain
        if request.subdomain:
            User = get_user_model()
            try:
                request.user = User.objects.get(username=request.subdomain)
                # Here you can record the visit or perform any other action you need
                if request.user.is_authenticated:
                    customer = Customer.objects.get(user=request.user)
                    customer.is_guest = False
                    customer.save()
            except User.DoesNotExist:
                raise Http404("User does not exist")

        # Continue with the normal request processing
        response = self.get_response(request)
        return response