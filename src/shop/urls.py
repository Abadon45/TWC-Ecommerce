
from django.urls import path
from django.views.generic import TemplateView
from .views import *

app_name='shop'

urlpatterns = [
    path('brand/', TemplateView.as_view(template_name='shop/brand.html'), name='brand'),
    path('category-2/', TemplateView.as_view(template_name='shop/category-2.html'), name='category_2'),
    path('category-3/', TemplateView.as_view(template_name='shop/category-3.html'), name='category_3'),
    path('category-4/', TemplateView.as_view(template_name='shop/category-4.html'), name='category_4'),
    path('category/', TemplateView.as_view(template_name='shop/category.html'), name='category'),
    path('compare/', TemplateView.as_view(template_name='shop/shop-compare.html'), name='compare'),
    path('search/', ShopView.as_view(), name='search'),
    path('promos/', ShopPromoBundleView.as_view(), name='promo'),
    path('single/<slug:slug>', ShopDetailView.as_view(), name='single'),
    path('single/get-review-details/<int:review_id>/', get_review_details, name='get_review_details'),
    path('single/edit-review/<int:review_id>/', edit_review, name='edit_review'),
    path('single/remove-review/<int:review_id>/', remove_review, name='remove_review'),
    path('', ShopView.as_view(), name='shop'),
]

