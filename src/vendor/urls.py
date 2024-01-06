
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from . import views

app_name='vendor'
urlpatterns = [
    path('dashboard/', TemplateView.as_view(template_name='vendor/seller.html'), name='vendor_dashboard'),
    path('invoice/', TemplateView.as_view(template_name='vendor/invoice.html'), name='invoice'),
    path('add-product/', TemplateView.as_view(template_name='vendor/vendor-add-product.html'), name='add_product'),

]
