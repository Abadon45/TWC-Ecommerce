
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView, RedirectView
from user.views import DashboardView
from django.conf import settings
from django.conf.urls.static import static

app_name='user'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)