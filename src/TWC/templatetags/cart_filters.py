from django import template

register = template.Library()

@register.filter
def get_cart_subtotal(items):
    """Calculate subtotal for the cart items."""
    return sum(float(item['product'].get('customer_price', 0)) * item['quantity'] for item in items)

