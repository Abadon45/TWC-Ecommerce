from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, ListView, DetailView
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.generic import ListView

from .models import Product, ProductImage
from .forms import ProductForm, ProductImageFormSet

import json

class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/add-product.html'
    success_url = reverse_lazy('products:product_list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        is_post = self.request.POST
        data['image_formset'] = ProductImageFormSet(self.request.POST, self.request.FILES) if is_post else ProductImageFormSet(queryset=ProductImage.objects.none())
        data['p'] = self.object if hasattr(self, 'object') else None
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']

        if image_formset.is_valid():
            self.object = form.save()
            image_formset.instance = self.object
            image_formset.save()
            if self.request.is_ajax():
                return JsonResponse({'redirect_url': self.success_url})
            else:
                return redirect(self.success_url)
        
        return self.render_to_response(self.get_context_data(form=form))
    

class ProductListView(ListView):
    model = Product
    template_name = 'products/product-list.html'
    context_object_name = 'products'
    paginate_by = 25

    def get_queryset(self):
        category = self.request.GET.get('category')
        if category:
            return Product.objects.filter(category=category).order_by('id')
        else:
            return Product.objects.all().order_by('id')

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()

        if self.request.is_ajax():
            products_data = [{'name': product.name, 'sku': product.sku, 'stock': product.stock, 'stock_unit': product.stock_unit,
                  'price': product.price, 'description': product.description, 'slug': product.slug, 'images': [{'image_url': image.image.url} for image in product.images.all()]}
                 for product in context['products']]
            return JsonResponse(products_data, safe=False)

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Product List'
        context['product_images'] = {product.id: product.images.first() for product in context['products']}
        context['categories'] = [
                {
                    'id': category_id,
                    'name': category_name,
                    'count': Product.objects.filter(category=category_id).count()
                }
                for category_id, category_name in Product.CATEGORY_CHOICES
            ]
        context['selected_category'] = int(self.request.GET.get('category', 0) or 0)
        context['selected_category_name'] = dict(Product.CATEGORY_CHOICES).get(context['selected_category'], 'Category')
        return context
    
class ProductDetailView(DetailView):
    model = Product
    template_name = 'shop/shop-single.html'
    context_object_name = 'product'

    
    def get_object(self, queryset=None):
        return get_object_or_404(Product, slug=self.kwargs['slug'])


    