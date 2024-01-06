from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, ListView, DetailView
from django.urls import reverse_lazy
from django.http import JsonResponse

# from cart.models import Cart

from .models import Product, ProductImage
from .forms import ProductForm, ProductImageFormSet

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
        return Product.objects.all().order_by('id')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Product List'
        context['product_images'] = {product.id: product.images.first() for product in context['products']}
        return context
    
class ProductDetailView(DetailView):
    model = Product
    template_name = 'shop/shop-single.html'
    context_object_name = 'product'

    
    def get_object(self, queryset=None):
        return get_object_or_404(Product, slug=self.kwargs['slug'])

    # def get_context_data(self, *args, **kwargs):
    #     context = super(ProductDetailView, self).get_context_data(*args, **kwargs)
    #     cart_obj, new_obj = Cart.objects.new_or_get(self.request)
    #     context['cart'] = cart_obj
    #     context['images'] = self.object.images.all()
    #     return context

    