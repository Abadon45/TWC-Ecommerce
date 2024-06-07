# custom_filters.py

from django import template

register = template.Library()

@register.filter(name='replace_underscore_to_space')
def replace_underscore_to_space(value):
    return value.upper().replace("_", " ")

@register.filter
def to(value, end):
    return range(value, end)
