# utils.py
import uuid

from billing.models import Customer


def create_or_get_guest_user(request):
    if request.user.is_authenticated:
        return request.user.customer if hasattr(request.user, 'customer') else None
    else:
        # Check if the guest user ID is stored in the cookie
        guest_user_id = request.session.get('guest_user_id')

        if guest_user_id:
            try:
                guest_user = Customer.objects.get(id=guest_user_id)
                if guest_user.user is not None:
                    request.session['guest_user'] = {
                        'username': guest_user.user.username,  # Assuming Customer has a foreign key to User
                        'email': guest_user.email,
                        'password': guest_user.user.password,  # Storing password in session is not recommended
                    }
                return guest_user
            except Customer.DoesNotExist:
                pass

        # If not, create a new guest user
        guest_user = Customer.objects.create(email=f'{uuid.uuid4()}@temporary.com')

        # Save guest user ID in a cookie
        request.session['guest_user_id'] = guest_user.id

        return guest_user
    
def get_or_create_customer(user):
    if hasattr(user, 'customer'):
        customer = user.customer
    else:
        customer, created = Customer.objects.get_or_create(user=user, defaults={'email': user.email})

    return customer
    