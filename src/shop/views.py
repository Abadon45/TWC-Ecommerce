from django.views.generic import View
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from products.views import ProductListView, ProductDetailView
from products.models import Product
from orders.models import Order
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.template.loader import render_to_string
from django.urls import NoReverseMatch
from django.db.models import Count

import random


class ShopView(ProductListView):
    model = Product
    template_name = 'shop/shop.html'
    context_object_name = 'products'
    paginate_by = 9
    _product_choices = None
    title = "Shop"

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
        elif category_id is None or category_id.lower() == 'all':
            queryset = Product.objects.filter(is_hidden=False)
        else:
            queryset = Product.objects.filter(category_1=category_id, is_hidden=False) | Product.objects.filter(category_2=category_id, is_hidden=False)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        order_ids = self.request.session.get('checkout_orders', [])
        orders = Order.objects.filter(id__in=order_ids)
        
        products_in_cart = [item.product_id for order in orders for item in order.orderitem_set.all()]

        if not self._product_choices:
            self._product_choices = {
                'categories_1': Product.PRODUCT_CATEGORY_1_CHOICES,
                'categories_2': Product.PRODUCT_CATEGORY_2_CHOICES,
            }
        context.update(self._product_choices)
        products = self.get_queryset()
        all_products = Product.objects.filter(is_hidden=False)
        subcategories = [
            'health_wellness',
            'healthy_beverages',
            'intimate_care',
            'bath_body',
            'watches',
            'bags',
            'accessories',
            # 'home_living',
        ]
        
        subcategory_counts = {subcategory: all_products.filter(category_2=subcategory).count() for subcategory in subcategories}
        
        subcategory_names = {
            subcategory: subcategory.replace('_', ' ')
            for subcategory in subcategories
        }

        context['products'] = products
        context['subcategory_counts'] =  subcategory_counts
        context['subcategory_names'] = subcategory_names
        context['products_in_cart'] =  products_in_cart
        context['title'] = self.title
        context['category_id'] = self.request.GET.get('category_id', '')
        context['q'] = self.request.GET.get('q', '')

        return context

    def render_to_response(self, context, **response_kwargs):
        page = self.request.GET.get('page', 1)
        paginator = Paginator(context['products'], self.paginate_by)

        try:
            paginated_products = paginator.page(page)
        except PageNotAnInteger:
            paginated_products = paginator.page(1)
        except EmptyPage:
            paginated_products = paginator.page(paginator.num_pages)
            
        if self.request.is_ajax():
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
            context['page_obj'] = paginated_products
            return super().render_to_response(context, **response_kwargs)


class ShopDetailView(ProductDetailView):
    template_name = "shop/shop-single.html"
    model = Product
    context_object_name = 'product'
    
    def get_object(self, queryset=None):
        return get_object_or_404(Product, slug=self.kwargs['slug'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        category_id = product.category_1
        
        order_ids = self.request.session.get('checkout_orders', [])
        orders = Order.objects.filter(id__in=order_ids)
        
        products_in_cart = [item.product_id for order in orders for item in order.orderitem_set.all()]
        
        # Get all related products except the current one
        related_products = Product.objects.filter(category_1=category_id).exclude(slug=product.slug)
        
        # Shuffle the queryset
        related_products = list(related_products)
        random.shuffle(related_products)
        
        # Limit the queryset to 4 items
        related_products = related_products[:4]
        
        context['related_products'] = related_products
        context['products_in_cart'] =  products_in_cart
        
        return context
    
class ShopPromoBundleView(View):
    template_name = "shop/shop-promo-bundle.html"

    def get(self, request, *args, **kwargs):
        products = [
            {
                'promo': 'promo1',
                'name': 'barley-for-cancer',
                'price': 2199,
                'quantity': 2,
                'image': 'img/product/promos/barley/barley-promo-1.png',
                'alt': 'promo 1',
                'name': 'Barley Promo 1',
            },
            {
                'promo': 'promo2',
                'name': 'barley-for-cancer',
                'price': 2299,
                'quantity': 3,
                'image': 'img/product/promos/barley/barley-promo-1.png',
                'alt': 'promo 2',
                'name': 'Barley Promo 2',
            },
            {
                'promo': 'promo3',
                'name': 'barley-for-cancer',
                'price': 2840,
                'quantity': 3,
                'image': 'img/product/promos/barley/barley-promo-1.png',
                'alt': 'promo 3',
                'name': 'Barley Promo 3',
            },
            {
                'promo': 'promo4',
                'name': 'weight-loss',
                'price': 799,
                'quantity': 2,
                'image': 'img/product/promos/barley/barley-promo-1.png',
                'alt': 'promo 4',
                'name': 'Fusion Coffee Promo 1',
            },
            {
                'promo': 'promo5',
                'name': 'weight-loss',
                'price': 1249,
                'quantity': 5,
                'image': 'img/product/promos/barley/barley-promo-1.png',
                'alt': 'promo 5',
                'name': 'Fusion Coffee Promo 2',
            },
            {
                'promo': 'promo6',
                'name': 'weight-loss',
                'price': 1649,
                'quantity': 7,
                'image': 'img/product/promos/barley/barley-promo-1.png',
                'alt': 'promo 6',
                'name': 'Fusion Coffee Promo 3',
            },
            {
                'promo': 'promo7',
                'name': 'boost-coffee',
                'price': 899,
                'quantity': 2,
                'image': 'img/product/promos/barley/barley-promo-1.png',
                'alt': 'promo 7',
                'name': 'Boost Coffee Promo 1',
            },
            {
                'promo': 'promo8',
                'name': 'boost-coffee',
                'price': 1349,
                'quantity': 5,
                'image': 'img/product/promos/barley/barley-promo-1.png',
                'alt': 'promo 8',
                'name': 'Boost Coffee Promo 2',
            },
            {
                'promo': 'promo9',
                'name': 'boost-coffee',
                'price': 1799,
                'quantity': 7,
                'image': 'img/product/promos/barley/barley-promo-1.png',
                'alt': 'promo 9',
                'name': 'Boost Coffee Promo 3',
            },

        ]

        # Example list of products in the cart
        products_in_cart = ['promo1'] 

        context = {
            'products': products,
            'products_in_cart': products_in_cart,
            'user': request.user,
        }
        return render(request, self.template_name, context)
    