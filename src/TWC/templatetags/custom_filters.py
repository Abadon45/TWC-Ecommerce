# custom_filters.py

from django import template
import math

register = template.Library()

@register.filter(name='replace_underscore_to_space')
def replace_underscore_to_space(value):
    return value.upper().replace("_", " ")

@register.filter
def to(value, end):
    return range(value, end)

@register.filter
def round_rating(value):
    try:
        return int(math.ceil(value) if value - int(value) >= 0.5 else math.floor(value))
    except (ValueError, TypeError):
        return value
    
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
