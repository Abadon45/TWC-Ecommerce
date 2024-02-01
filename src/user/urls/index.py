
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView, RedirectView
from user.views import DashboardView

app_name='user'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
]
