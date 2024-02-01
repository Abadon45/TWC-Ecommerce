#url_with_domain.py

from django import template
from django.urls import reverse

register = template.Library()

@register.simple_tag(takes_context=True)
def url_with_domain(context, view_name, *args, **kwargs):
    url = reverse(view_name, args=args, kwargs=kwargs)
    return context['MAIN_SITE_URL'] + url