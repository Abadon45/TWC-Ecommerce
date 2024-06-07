from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, ListView, DetailView
from django.views import View
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView

from .models import Product, Rating
from .forms import ProductForm

from django.db.models import Avg




class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/add-product.html'
    success_url = reverse_lazy('products:product_list')

    def form_valid(self, form):
        response = super().form_valid(form)

        for i in range(1, 6):
            image_field = f'image_{i}'
            image = self.request.FILES.get(image_field)
            if image:
                setattr(self.object, image_field, image)

        self.object.save()

        if self.request.is_ajax():
            return JsonResponse({'redirect_url': self.success_url})
        else:
            return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        print("Form Errors:", form.errors)

        return response


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


class RateProductView(View):
    def post(self, request, *args, **kwargs):
        product_id = kwargs.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        score = request.POST.get('score')

        if score is not None and request.user.is_authenticated:
            rating, created = Rating.objects.get_or_create(user=request.user, product=product)
            rating.score = score
            rating.save()

            # Calculate the new average rating
            average_rating = Rating.objects.filter(product=product).aggregate(Avg('score'))['score__avg']
            return JsonResponse({'average_rating': average_rating})

        return JsonResponse({'error': 'Invalid data'}, status=400)