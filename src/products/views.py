from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, ListView, DetailView
from django.core.serializers import serialize
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.generic import ListView

from .models import Product
from .forms import ProductForm

import json

def product_create_view(request):
    template_name = 'products/add-product.html'
    success_url = reverse_lazy('products:product_list')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)

        # For debugging purposes, print form data
        print("Form Data:", request.POST)

        if form.is_valid():
            print("Form is valid")

            product_instance = form.save()

            if request.is_ajax():
                return JsonResponse({'redirect_url': success_url})
            else:
                return redirect(success_url)

        else:
            print("Form is not valid")
            print("Form Errors:", form.errors)

    else:
        form = ProductForm()

    products = Product.objects.all().values('name', 'sku', 'image_1')

    return render(request, template_name, {'form': form, 'products': products})


class ProductListView(ListView):
    model = Product
    template_name = 'products/product-list.html'
    context_object_name = 'products'
    paginate_by = 25

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        return context
    
class ProductDetailView(DetailView):
    model = Product
    template_name = 'shop/shop-single.html'
    context_object_name = 'product'

    
    def get_object(self, queryset=None):
        return get_object_or_404(Product, slug=self.kwargs['slug'])


    