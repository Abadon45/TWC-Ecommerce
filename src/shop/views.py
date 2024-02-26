from django.views.generic import View
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from products.views import ProductListView, ProductDetailView
from products.models import Product
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.template.loader import render_to_string
from django.urls import NoReverseMatch
from django.db.models import Count



class ShopView(ProductListView):
    model = Product
    template_name = 'shop/shop.html'
    context_object_name = 'products'
    paginate_by = 9
    _product_choices = None
    
    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except NoReverseMatch:
            # Handle the exception here
            return HttpResponse("An error occurred")

    def get_queryset(self):
        category_id = self.request.GET.get('category_id')
        search_query = self.request.GET.get('q')

        if search_query:
            queryset = Product.objects.filter(name__icontains=search_query)
            print(f"Search results: {queryset}")  # Print the search results
        elif category_id is None or category_id.lower() == 'all':
            queryset = Product.objects.all()
        else:
            queryset = Product.objects.filter(category_1=category_id) | Product.objects.filter(category_2=category_id)
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
        subcategories = ['sante-nutraceutical', 'sante-beverage', 'sante-intimate_care']
        
        # Filter products by subcategories
        filtered_products = products.filter(category_2__in=subcategories)

        # Count the number of products in each subcategory and replace hyphens with underscores in the keys
        subcategory_counts = {subcategory.replace('-', '_'): filtered_products.filter(category_2=subcategory).count() for subcategory in subcategories}

        # Print the subcategory_counts dictionary to the console
        print(subcategory_counts)

        context['products'] = products
        context['subcategory_counts'] = subcategory_counts

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

            serialized_products = [
                {
                    'name': product.name,
                    'description': product.description_1,
                    'price': product.customer_price,
                    'image': product.image_1.url if product.image_1 else '',
                    'slug': product.slug,
                    'id': product.id,

                }
                for product in paginated_products
            ]
            
            products_grid_html = render_to_string('shop/products_grid.html', {'page_obj': paginated_products}, request=self.request)
            products_list_html = render_to_string('shop/products_list.html', {'page_obj': paginated_products}, request=self.request)
            pagination_html = render_to_string('shop/pagination.html', {'page_obj': paginated_products}, request=self.request)

            response_data = {
                'products': serialized_products,
                'has_next': paginated_products.has_next(),
                'has_previous': paginated_products.has_previous(),
                'products_grid_html': products_grid_html,
                'products_list_html': products_list_html,
                'pagination_html': pagination_html,
            }
            
            return JsonResponse(response_data)
        else:
            return super().render_to_response(context, **response_kwargs)
        

class ShopDetailView(ProductDetailView):
    template_name = "shop/shop-single.html"
    
    def get_object(self, queryset=None):
        return get_object_or_404(Product, slug=self.kwargs['slug'])
    