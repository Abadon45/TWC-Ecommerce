from django import template

register = template.Library()

@register.filter
def currency(value):
    try:
        value = float(value)  # Convert the value to float
    except (ValueError, TypeError):
        return value  # Return the original value if it can't be converted to float
    return f"₱{value:,.2f}"