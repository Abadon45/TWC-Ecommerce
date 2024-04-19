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
    
def booking_count_notification(request):
    booking_count = Order.objects.filter(status='for-booking').count()
    mandaluyong_count = Order.objects.filter(status='for-booking', courier__fulfiller='sante mandaluyong').count()
    valenzuela_count = Order.objects.filter(status='for-booking', courier__fulfiller='sante valenzuela').count()
    cdo_count = Order.objects.filter(status='for-booking', courier__fulfiller='sante cdo').count()
    other_count = Order.objects.filter(status='for-booking', courier__fulfiller='other').count()
    return {
        'booking_count': booking_count,
        'mandaluyong_count': mandaluyong_count,
        'valenzuela_count':  valenzuela_count,
        'cdo_count': cdo_count,
        'other_count': other_count,
    }
    
def pickup_count_notification(request):
    pickup_count = Order.objects.filter(status='for-pickup').count()
    return{'pickup_count': pickup_count}

def return_count_notification(request):
    return_count = Order.objects.filter(status='rts').count()
    return{'return_count': return_count}