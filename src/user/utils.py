# utils.py
import uuid

from billing.models import Customer
from orders.models import Order


def create_or_get_guest_user(request):
    if request.user.is_authenticated:
        return request.user.customer if hasattr(request.user, 'customer') else None
    else:
        guest_user = None
        guest_user_id = request.session.get('guest_user_id')

        if guest_user_id:
            try:
                guest_user = Customer.objects.get(id=guest_user_id)
                has_existing_orders = Order.objects.filter(customer=guest_user).exists()
                request.session['new_guest_user'] = not has_existing_orders
                request.session['has_existing_order'] = has_existing_orders
                request.session.modified = True
                guest_user.is_guest = True
                guest_user.save()
                return guest_user
            except Customer.DoesNotExist:
                del request.session['guest_user_id']

        if not guest_user:
            guest_user = Customer.objects.create(email=f'{uuid.uuid4()}@temporary.com', is_guest=True)
            request.session['guest_user_id'] = guest_user.id
            request.session['new_guest_user'] = True
            request.session['has_existing_order'] = False
            request.session.modified = True

        return guest_user
    
def get_or_create_customer(user):
    if hasattr(user, 'customer'):
        customer = user.customer
    else:
        customer, created = Customer.objects.get_or_create(user=user, defaults={'email': user.email})

    return customer
    