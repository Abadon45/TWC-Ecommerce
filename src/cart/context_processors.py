from cart.models import *
from django.contrib.auth import get_user_model


User = get_user_model()

def cart_items(request):
    try: 
        order_ids = request.session.get('checkout_orders', [])
        orders = Order.objects.filter(id__in=order_ids)
        
        cart_items = sum(order.total_quantity for order in orders)
        
        ordered_items = {}
        for order in orders:
            ordered_items[order] = OrderItem.objects.filter(order=order).select_related('product')
            
        total_cart_subtotal = sum(order.calculate_subtotal() for order in orders)
            
        return {
            'cart_items': cart_items,
            'orders': orders,
            'ordered_items': ordered_items,
            'total_cart_subtotal': total_cart_subtotal,
            }

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
    
def pending_orders_notification(request):
    user = request.user
    pending_orders_count = 0
    orders_count = 0
    
    if user.is_authenticated and user.is_staff:
        referred_users = User.objects.filter(referred_by=user)
        orders = Order.objects.filter(user__in=referred_users, delivered=False)
        
        pending_orders_count = orders.count()
        orders_count = orders.count()
    
    return{
        'pending_orders_count':pending_orders_count,
        'orders_count': orders_count,
    }
    
def booking_count_notification(request):
    user = request.user
    booking_count = 0
    mandaluyong_count = 0
    valenzuela_count = 0
    cdo_count = 0
    other_count = 0
    
    if user.is_authenticated and user.is_staff:
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
    user = request.user
    pickup_count = 0
    
    if user.is_staff:
        pickup_count = Order.objects.filter(status='for-pickup').count()
    return{'pickup_count': pickup_count}

def return_count_notification(request):
    user = request.user
    return_count = 0
    
    if user.is_staff:
        return_count = Order.objects.filter(status='rts').count()
    return{'return_count': return_count}