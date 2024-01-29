# utils.py
import uuid

from billing.models import Customer
from orders.models import Order


def create_or_get_guest_user(request):
    if request.user.is_authenticated:
        return request.user.customer if hasattr(request.user, 'customer') else None
    else:
        # Check if the guest user ID is stored in the cookie
        guest_user_id = request.session.get('guest_user_id')

        if guest_user_id:
            try:
                guest_user = Customer.objects.get(id=guest_user_id)
                has_existing_orders = Order.objects.filter(customer=guest_user).exists()
                request.session['new_guest_user'] = not has_existing_orders
                request.session['has_existing_order'] = has_existing_orders
                print('session', request.session['new_guest_user'])
                return guest_user
            except Customer.DoesNotExist:
                pass

        # If not, create a new guest user
        guest_user = Customer.objects.create(email=f'{uuid.uuid4()}@temporary.com')

        # Save guest user ID in a cookie
        request.session['guest_user_id'] = guest_user.id
        
        # Set a flag in the session to indicate that this is a new guest user
        request.session['new_guest_user'] = True

        # Set a flag in the session to indicate that this guest user does not have any existing orders
        request.session['has_existing_order'] = False

        return guest_user
    
def get_or_create_customer(user):
    if hasattr(user, 'customer'):
        customer = user.customer
    else:
        customer, created = Customer.objects.get_or_create(user=user, defaults={'email': user.email})

    return customer
    