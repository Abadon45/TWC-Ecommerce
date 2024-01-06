
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView, RedirectView
from .views import DashboardView

app_name='user'
urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]
