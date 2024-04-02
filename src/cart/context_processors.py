from orders.models import Order
from django.contrib.auth import get_user_model
from django.http import JsonResponse


User = get_user_model()

def cart_items(request):
    try: 
        order_ids = request.session.get('checkout_orders', [])
        orders = Order.objects.filter(id__in=order_ids)
        
        cart_items = sum(order.total_quantity for order in orders)
        
        for order in orders:
            print(f"Existing order_id: {order.order_id}")
        
        return {'cart_items': cart_items}

    except Order.DoesNotExist:
        return {'cart_items': 0}
    except Exception as e:
        print(f"Error in cart_items view: {e}")
        return {'cart_items': 0}
                
def new_guest_user(request):
    return {'new_guest_user': request.session.get('new_guest_user', False)}

def has_existing_order(request):
    return {
        'has_existing_order': request.session.get('has_existing_order', False)
    }