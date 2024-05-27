# hosts.py

from django.conf import settings
from django_hosts import host


host_patterns = [
    host(r'admin', 'TWC.urls.admin', name='admin'),
    host(r'dashboard', 'TWC.urls.dashboard', name='dashboard'),
    host(r'www', 'TWC.urls', name='www'),
    host(r'', 'TWC.urls', name='www'),
] 
