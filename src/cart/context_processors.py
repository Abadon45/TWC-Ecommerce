from orders.models import Order
from user.utils import create_or_get_guest_user
from django.contrib.auth import get_user_model

User = get_user_model()

def cart_items(request):
    cart_items_count = 0
    subtotal = 0
    shipping = 0
    discount = 0
    total = 0
    items = []
    order_id = None
    
    user = request.user

    try:

        if user.is_authenticated:
            orders = Order.objects.filter(user=user, complete=False)
        else:
            session_key = request.session.session_key
            orders = Order.objects.filter(session_key=session_key, complete=False)
        

        if orders.exists():
            order = orders.first()
            cart_items_count = order.get_cart_total
            subtotal = order.get_cart_items
            shipping = order.shipping_fee
            total = subtotal - discount + shipping
            items = order.orderitem_set.all()
            order_id = order.order_id

    except Order.DoesNotExist:
        order = None

    print(f"Existing order_id: {order_id}")

    return {
        'cart_items': cart_items_count,
        'items': items,
        'subtotal': subtotal,
        'discount': discount,
        'shipping': shipping,
        'total': total,
        'order_id': order_id,
    }

def new_guest_user(request):
    return {'new_guest_user': request.session.get('new_guest_user', False)}

def has_existing_order(request):
    return {
        'has_existing_order': request.session.get('has_existing_order', False)
    }