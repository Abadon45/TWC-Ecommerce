from orders.models import Order

def cart_items(request):
    cart_items_count = 0
    subtotal = 0
    shipping = 0
    discount = 0
    total = 0
    items = []
    order_id = None

    if request.user.is_authenticated:
        customer = request.user.customer

        try:
            order = Order.objects.get(customer=customer, complete=False)
            cart_items_count = order.get_cart_total
            subtotal = order.get_cart_items
            total = subtotal - discount + shipping
            items = order.orderitem_set.all()
            order_id = order.order_id
        except Order.DoesNotExist:
            order = None

        print(f"Authenticated user, Existing order_id: {order_id}")

    return {
        'cart_items': cart_items_count,
        'items': items,
        'subtotal': subtotal,
        'discount': discount,
        'shipping': shipping,
        'total': total,
        'order_id': order_id,
    }
