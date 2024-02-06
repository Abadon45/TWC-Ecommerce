# utils.py
import uuid

from django.contrib.auth import get_user_model
from billing.models import Customer
from orders.models import Order


User = get_user_model()

def create_or_get_guest_user(request, referrer_id=None):
    referrer_id = request.session.get('referrer_id')
    referrer=User.objects.get(id=referrer_id) if referrer_id else None
    if request.user.is_authenticated:
        customer = request.user.customer if hasattr(request.user, 'customer') else None
        if customer:
            customer.referrer = referrer
            customer.save()
        return customer
    else:
        guest_user = None
        guest_user_id = request.session.get('guest_user_id')

        if guest_user_id:
            try:
                guest_user = Customer.objects.get(id=guest_user_id)
                has_existing_orders = Order.objects.filter(customer=guest_user).exists()
                request.session['new_guest_user'] = not has_existing_orders
                request.session['guest_order'] = has_existing_orders
                request.session.modified = True
                if referrer:
                    guest_user.referrer = referrer
                guest_user.save()
                return guest_user
            except Customer.DoesNotExist:
                del request.session['guest_user_id']

        if not guest_user:
            guest_user = Customer.objects.create(email=f'{uuid.uuid4()}@temporary.com', is_guest=True)
            request.session['guest_user_id'] = guest_user.id
            request.session['new_guest_user'] = True
            request.session['guest_order'] = False
            request.session.modified = True

        return guest_user
    
def get_or_create_customer(request, user, referrer_id=None):
    if user.is_authenticated:
        user.save()  # Ensure the User object exists in the database
        if hasattr(user, 'customer'):
            customer = user.customer
        else:
            customer, created = Customer.objects.get_or_create(user=user, defaults={'email': user.email})
        return customer
    else:
        if referrer_id is not None:
            referrer = User.objects.get(id=referrer_id)
        else:
            referrer = None

        customer = create_or_get_guest_user(request, referrer=referrer)
        return customer
    