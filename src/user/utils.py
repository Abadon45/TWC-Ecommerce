# utils.py
import uuid
import json
from billing.models import Customer
from django.contrib.auth.models import AnonymousUser
from django.http import JsonResponse


def create_or_get_guest_user(request):
    if request.user.is_authenticated:
        return request.user.customer if hasattr(request.user, 'customer') else None
    else:
        
        guest_user_email = request.COOKIES.get('guest_user')

        if guest_user_email:
            customer = Customer.objects.filter(email=guest_user_email).first()
            if customer:
                return customer

        guest_user_email = f'{uuid.uuid4()}@temporary.com'
        
        # Use AnonymousUser for guest users
        guest_user = AnonymousUser()
        guest_user.customer = Customer.objects.create(email=guest_user_email)
        
        # Save guest user email in a cookie
        response = JsonResponse({'status': 'success'})
        response.set_cookie('guest_user', guest_user_email, max_age=60*60*24*7)  # Set the cookie to expire in 7 days

        return guest_user.customer
