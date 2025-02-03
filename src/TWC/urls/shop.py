
from django.urls import path
from django.views.generic import TemplateView
from onlinestore.views.shop import *
from onlinestore.utils import fetch_address_data, fetch_category_count

app_name='shop'

urlpatterns = [

    path('', ShopView.as_view(), name='shop'),
    path('brand/', TemplateView.as_view(template_name='shop/brand.html'), name='brand'),
    path('search/', ShopView.as_view(), name='search'),
    path('single/<slug:slug>/', ShopDetailView.as_view(), name='single'),

    #API
    path('api/get-address/', fetch_address_data, name='get_address_data'),
    path('api/fetch-category-count', fetch_category_count, name='fetch_category_count'),
]

