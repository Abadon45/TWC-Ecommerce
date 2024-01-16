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

        category_param = self.request.GET.get('category', 'all')
        context['selected_category'] = category_param  # Default to 'all'

        if category_param.lower() != 'all':
            try:
                # Attempt to convert to integer if not 'all'
                context['selected_category'] = int(category_param)
            except ValueError:
                # Handle invalid category values
                # Set selected_category to 'all' or another default value
                context['selected_category'] = 'all'

        context['title'] = 'Shop'
        context['categories'] = [
            {
                'id': category_id,
                'name': category_name,
                'count': Product.objects.filter(category=category_id).count()
            }
            for category_id, category_name in Product.CATEGORY_CHOICES
        ]
        context['selected_category_name'] = dict(Product.CATEGORY_CHOICES).get(context['selected_category'], 'Category')
        return context





class ShopDetailView(ProductDetailView):
    template_name = "shop/shop-single.html"
