from django.views.generic import View
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.template.loader import render_to_string
from django.urls import NoReverseMatch
from django.db.models import Count
from django.contrib.auth import get_user_model
from django.utils.timezone import now

from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from products.views import ProductListView, ProductDetailView
from products.models import Product, Rating, Review
from products.forms import RatingForm, ReviewForm
from orders.models import Order

import random

User = get_user_model()


class ShopView(ProductListView):
    model = Product
    template_name = 'shop/shop.html'
    context_object_name = 'products'
    paginate_by = 9
    _product_choices = None
    title = "Shop"

    def get(self, request, *args, **kwargs):
        try:
            referrer_username = request.GET.get('username', None)
            
            if referrer_username:
                referrer = User.objects.filter(username=referrer_username).first()
                if not referrer or referrer_username == 'admin':
                    return redirect(reverse_lazy('handle_404'))

                request.session['referrer'] = referrer_username
                print(f"Username in shop session: {request.session.get('referrer')}")
            
            return super().get(request, *args, **kwargs)
        except Exception as e:
            return HttpResponse(f"An error occurred: {str(e)}")

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

    def get_user_ratings(self, products):
        user_ratings = {}
        if self.request.user.is_authenticated:
            for product in products:
                user_ratings[product.id] = None  # Default value in case no rating exists for a product
                try:
                    rating = Rating.objects.get(product=product, user=self.request.user)
                    user_ratings[product.id] = rating.score 
                except Rating.DoesNotExist:
                    pass  
        return user_ratings

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

        # This line ensures that `self.get_queryset()` is called to update the context with the queryset of products
        context['products'] = self.get_queryset()

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
        
        # Get the user ratings for products on the current page
        user_ratings = self.get_user_ratings(context['page_obj'])
        print(f'User Ratings: {user_ratings}')
        
        context['subcategory_counts'] = subcategory_counts
        context['subcategory_names'] = subcategory_names
        context['products_in_cart'] = products_in_cart
        context['title'] = self.title
        context['category_id'] = self.request.GET.get('category_id', '')
        context['q'] = self.request.GET.get('q', '')
        context['user_ratings'] = user_ratings

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
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()

        # Get related products
        related_products = Product.objects.filter(category_1=product.category_1).exclude(slug=product.slug).order_by('?')[:4]

        # Get products in cart
        order_ids = self.request.session.get('checkout_orders', [])
        orders = Order.objects.filter(id__in=order_ids)
        products_in_cart = [item.product_id for order in orders for item in order.orderitem_set.all()]

        # Get user rating for the product if authenticated
        rating = None
        user_reviewed = False
        if self.request.user.is_authenticated:
            try:
                rating = Rating.objects.get(product=product, user=self.request.user)
            except Rating.DoesNotExist:
                rating = None
            
        user_reviewed = Rating.objects.filter(product=product, user=self.request.user).exists()

        # Get all product ratings
        product_ratings = Rating.objects.filter(product=product)
        

        # Get product reviews
        product_reviews = product.reviews.select_related('rating').all()
        for review in product_reviews:
            if review.created_at is None:
                review.created_at = now()
                print(review.create_at)
                review.save()

        # Forms
        context['rating_form'] = RatingForm()
        context['review_form'] = ReviewForm()

        # Context variables
        context['related_products'] = related_products
        context['products_in_cart'] = products_in_cart
        context['rating'] = rating
        context['user_reviewed'] = user_reviewed
        context['product_reviews'] = product_reviews
        context['product_ratings'] = product_ratings

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Handle Rating Form submission
        rating_form = RatingForm(request.POST)
        review_form = ReviewForm(request.POST)

        if rating_form.is_valid() and review_form.is_valid():
            # Ensure a unique rating and review pair
            try:
                rating = Rating.objects.get(product=self.object, user=request.user)
                rating.score = rating_form.cleaned_data['score']
                rating.save()
            except Rating.DoesNotExist:
                rating = rating_form.save(commit=False)
                rating.user = request.user
                rating.product = self.object
                rating.save()

            try:
                review = Review.objects.get(product=self.object, user=request.user)
                review.content = review_form.cleaned_data['content']
                review.rating = rating
                review.save()
            except Review.DoesNotExist:
                review = review_form.save(commit=False)
                review.user = request.user
                review.product = self.object
                review.rating = rating
                review.save()

            return redirect('shop:single', slug=self.object.slug)

        # If neither form is valid, render the context with errors
        context = self.get_context_data(object=self.object)
        context['rating_form'] = rating_form
        context['review_form'] = review_form
        return self.render_to_response(context)
    
@login_required
def get_review_details(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    rating = Rating.objects.get(review=review)
    return JsonResponse({'content': review.content, 'rating': rating.score})
    
@login_required
@require_POST
def edit_review(request, review_id):
    try:
        print(f"Request Method: {request.method}")
        print(f"Review ID: {review_id}")
        
        review = get_object_or_404(Review, id=review_id, user=request.user)
        print(f"Review found: {review}")
        
        # Update the review content
        review.content = request.POST.get('content')
        review.save()
        
        # Update the rating
        rating = review.rating
        rating.score = request.POST.get('rating')
        rating.save()
        
        print("Form is valid and saved")
        return JsonResponse({'success': True, 'message': 'Review updated successfully!'})
    except Exception as e:
        print(f"Exception: {e}")
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
@require_POST
def remove_review(request, review_id):
    try:
        review = get_object_or_404(Review, id=review_id, user=request.user)
        if hasattr(review, 'rating'):
            review.rating.delete()
        review.delete()
        return JsonResponse({'success': True, 'message': 'Review removed successfully!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

    
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
    