from django.views.generic import View, TemplateView
from django.shortcuts import render
from products.views import ProductListView, ProductDetailView
from products.models import Product


class ShopView(ProductListView):
    template_name = 'shop/shop.html'
    context_object_name = 'products'
    paginate_by = 25


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


class ShopDetailView(ProductDetailView):
    template_name = "shop/shop-single.html"
