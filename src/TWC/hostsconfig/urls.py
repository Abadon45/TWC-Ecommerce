from django.urls import path
from .views import www_root_redirect

urlpatterns = [
    path('', www_root_redirect),
]