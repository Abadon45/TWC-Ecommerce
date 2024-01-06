from django.views.generic import View, TemplateView
from django.shortcuts import render
from products.views import ProductListView, ProductDetailView


class ShopGridView(ProductListView):
    template_name = 'shop/shop-grid.html'
    title = 'Shop Grid'
    
class ShopListView(ProductListView):
    template_name = 'shop/shop-list.html'
    title = 'Shop List'
    
class ShopDetailView(ProductDetailView):
    template_name = "shop/shop-single.html"

