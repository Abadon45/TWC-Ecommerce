# hosts.py

from django.conf import settings
from django_hosts import host

host_patterns = [
    host(r'admin', 'TWC.urls.admin', name='admin'),
    host(r'dashboard', 'TWC.urls.dashboard', name='dashboard'),
    host(r'(?P<username>\w+)', 'TWC.urls', name='wildcard'),
]
