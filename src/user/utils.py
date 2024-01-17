# utils.py
import uuid
from billing.models import Customer
from django.contrib.sessions.models import Session

def create_or_get_guest_user(request):
    if request.user.is_authenticated:
        # Use get() with a default value to handle the case where customer doesn't exist
        return request.user.customer if hasattr(request.user, 'customer') else None
    else:
        session_key = request.session.session_key
        guest_user_email = request.session.get('guest_user')

        if guest_user_email:
            customer = Customer.objects.filter(email=guest_user_email).first()
            if customer:
                return customer

        identifier = str(uuid.uuid4())
        guest_user_email = f'temporary_email_{identifier}@example.com'
        customer, created = Customer.objects.get_or_create(email=guest_user_email)

        request.session['guest_user'] = guest_user_email
        return customer
