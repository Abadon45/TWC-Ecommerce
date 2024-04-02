from django import template

register = template.Library()

@register.filter
def currency(value):
    return f"₱{value:,.2f}" 