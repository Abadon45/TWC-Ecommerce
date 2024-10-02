from django.urls import path
from onlinestore.views import subdomain_view

urlpatterns = [
    path('', subdomain_view, name='subdomain'),
]
