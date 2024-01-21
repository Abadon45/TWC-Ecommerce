from django.views.generic import View
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from products.views import ProductListView, ProductDetailView
from products.models import Product
from django.http import JsonResponse
from django.db.models import Q


class ShopView(ProductListView):
    model = Product
    template_name = 'shop/shop.html'
    context_object_name = 'products'
    paginate_by = 25
    _product_choices = None


    def get_queryset(self):
        category_id = self.request.GET.get('category_id')
        
        if category_id is None or category_id.lower() == 'all':
            queryset = Product.objects.all()
        else:
            queryset = Product.objects.filter(category_1=category_id) | Product.objects.filter(category_2=category_id)
        
        print(f"Category ID: {category_id}")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if not self._product_choices:
            self._product_choices = {
                'categories_1': Product.PRODUCT_CATEGORY_1_CHOICES,
                'categories_2': Product.PRODUCT_CATEGORY_2_CHOICES,
            }
        context.update(self._product_choices)
        products = self.get_queryset()
        print(f"Products length in context: {len(products)}")
        context['products'] = products
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.is_ajax():
            # Pagination logic for AJAX requests
            page = self.request.GET.get('page', 1)
            paginator = Paginator(context['products'], self.paginate_by)

            try:
                paginated_products = paginator.page(page)
            except PageNotAnInteger:
                paginated_products = paginator.page(1)
            except EmptyPage:
                paginated_products = paginator.page(paginator.num_pages)

            # Convert paginated_products to a format that can be serialized
            serialized_products = [
                {
                    'name': product.name,
                    'description': product.description_1,
                    'price': product.customer_price,
                    'image': product.image_1.url if product.image_1 else '',
                    'slug': product.slug,

                }
                for product in paginated_products
            ]

            response_data = {
                'products': serialized_products,
                'has_next': paginated_products.has_next(),
                'has_previous': paginated_products.has_previous(),
            }
            print(f"AJAX Response: {response_data}")
            
            return JsonResponse(response_data)
        else:
            return super().render_to_response(context, **response_kwargs)

class ShopDetailView(ProductDetailView):
    template_name = "shop/shop-single.html"
    