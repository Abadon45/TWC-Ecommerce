# custom_filters.py

from django import template
import math
import logging

register = template.Library()

@register.filter(name='replace_underscore_to_space')
def replace_underscore_to_space(value):
    return value.upper().replace("_", " ")

@register.filter(name='replace_underscore_to_dash')
def replace_underscore_to_space(value):
    return value.upper().replace("_", "-")

@register.filter
def to(value, end):
    return range(value, end)

@register.filter
def subtract(value, arg):
    return value - arg

@register.filter
def round_rating(value):
    try:
        return int(math.ceil(value) if value - int(value) >= 0.5 else math.floor(value))
    except (ValueError, TypeError):
        return value
    
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def increase_by_10_percent(value):
    try:
        value = float(value)
        new_value = value * 1.10
        logging.warning(f"Original value: {value}, Increased value: {new_value}")
        return new_value
    except (ValueError, TypeError) as e:
        logging.error(f"Error in increase_by_10_percent: {e}")
        return value