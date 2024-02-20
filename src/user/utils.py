# utils.py
import uuid

from django.contrib.auth import get_user_model
from django.apps import apps

User = get_user_model()

def create_or_get_guest_user(request, referrer_id=None):
    guest_user_id = request.session.get('guest_user_id')
    Customer = apps.get_model('billing', 'Customer')
    if guest_user_id:
        try:
            guest_customer = Customer.objects.get(id=guest_user_id)
            print("Returning existing guest user: ", guest_customer.id)
            return guest_customer
        except Customer.DoesNotExist:
            print("No customer found with id: ", guest_user_id)
            del request.session['guest_user_id']

    # Create a new Customer instance
    guest_user_email = f'{str(uuid.uuid4())[:8]}@temporary.com'
    referrer = User.objects.get(id=referrer_id) if referrer_id else None
    guest_customer = Customer.objects.create(email=guest_user_email, referrer=referrer)
    request.session['guest_user_id'] = guest_customer.id
    request.session['new_guest_user'] = True
    request.session['guest_order'] = False
    request.session.modified = True
    print("Created new guest user: ", guest_customer.id)

    return guest_customer
    
@classmethod
def get_or_create_customer(cls, user, request, referrer_code=None):
    print("Entering get_or_create_customer method")
    referrer = None
    
    if referrer_code:
        try:
            # Try to get User by id
            referrer = User.objects.get(id=int(referrer_code))
        except (ValueError, User.DoesNotExist):
            # If referrer_code is not an integer or User does not exist, try getting User by username
            try:
                referrer = User.objects.get(username=referrer_code)
            except User.DoesNotExist:
                referrer = None
                
    if user.is_authenticated:
        user.save()  # Ensure the User object exists in the database
        if hasattr(user, 'customer'):
            customer = user.customer
        else:
            Customer = apps.get_model('billing', 'Customer')
            customer, created = Customer.objects.get_or_create(user=user, defaults={'email': user.email})
        print(f"Authenticated user: {user}, Customer: {customer}")  # Print statement for debugging
        return customer
    else:
        referrer_id = referrer.id if referrer else None

        guest_customer = create_or_get_guest_user(request, referrer_id=referrer_id)  # This is a Customer instance
        print(f"Guest customer: {guest_customer}, Type: {type(guest_customer)}")  # Print statement for debugging
        Customer = apps.get_model('billing', 'Customer')
        customer, created = Customer.objects.get_or_create(email=guest_customer.email, user=guest_customer.user, defaults={'is_guest': True, 'referrer': referrer})
        print(f"Created customer: {customer}, Created: {created}")  # Print statement for debugging

    return customer