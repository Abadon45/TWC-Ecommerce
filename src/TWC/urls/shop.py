
from django.urls import path
from django.views.generic import TemplateView
from onlinestore.views.shop import *
from onlinestore.utils import fetch_address_data

app_name='shop'

urlpatterns = [
    path('brand/', TemplateView.as_view(template_name='shop/brand.html'), name='brand'),
    path('search/', ShopView.as_view(), name='search'),
    # path('promos/', ShopPromoBundleView.as_view(), name='promo'),
    path('single/<slug:slug>/', ShopDetailView.as_view(), name='single'),
    # path('single/get-review-details/<int:review_id>/', get_review_details, name='get_review_details'),
    # path('single/edit-review/<int:review_id>/', edit_review, name='edit_review'),
    # path('single/remove-review/<int:review_id>/', remove_review, name='remove_review'),
    path('', ShopView.as_view(), name='shop'),

    #API
    path('api/get-address/', fetch_address_data, name='get_address_data'),
]

