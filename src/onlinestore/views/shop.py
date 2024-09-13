from django.views.generic import View
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import redirect
from django.http import JsonResponse, Http404
from django.db.models import Q
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.utils.timezone import now

from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from products.views import ProductListView, ProductDetailView
from products.models import Product, Rating, Review
from products.forms import RatingForm, ReviewForm
from cart.models import Order, OrderItem
from onlinestore.utils import check_sponsor_and_redirect
from collections import defaultdict

import requests
import random

User = get_user_model()


class ShopView(ProductListView):
    model = Product
    template_name = 'shop/shop.html'
    context_object_name = 'products'
    paginate_by = 9
    _product_choices = None
    title = "Shop"

    def get(self, request, username=None, *args, **kwargs):
        if username:
            return check_sponsor_and_redirect(request, username, 'shop:shop')

            # If username is not provided, proceed with the normal GET handling
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        category_id = self.request.GET.get('category_id')
        search_query = self.request.GET.get('q')
        sort_option = self.request.GET.get('sort', '1')
        queryset = []


        api_url = 'https://dashboard.twcako.com/shop/api/get-product/'

        try:
            # Make the API request
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()

            if data.get("success"):
                queryset = data.get("products", [])


                # Filter by search query if provided
                if search_query:
                    queryset = [
                        product for product in queryset
                        if search_query.lower() in product.get('name', '').lower()
                           or search_query.lower() in product.get('category_1', '').lower()
                           or search_query.lower() in product.get('category_2', '').lower()
                    ]

                # Filter by category if provided
                if category_id and category_id.lower() != 'all':
                    queryset = [
                        product for product in queryset
                        if product.get('category_1') == category_id or product.get('category_2') == category_id
                    ]

                # Sorting logic
                if sort_option == '5':  # Latest Items
                    queryset = sorted(queryset, key=lambda p: p.get('timestamp', ''), reverse=True)
                elif sort_option == '3':  # Price - Low To High
                    queryset = sorted(queryset, key=lambda p: p.get('customer_price', 0))
                elif sort_option == '4':  # Price - High To Low
                    queryset = sorted(queryset, key=lambda p: p.get('customer_price', 0), reverse=True)

            return queryset
        except requests.exceptions.RequestException as e:
            # Handle API request errors
            return JsonResponse({'error': str(e)})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sort_option = self.request.GET.get('sort', '1')
        page = self.request.GET.get('page', 1)
        category_product_count = defaultdict(int)

        # Fetch the products from the API using the get_queryset method
        products = self.get_queryset()

        # Count products in each subcategory
        for product in products:
            subcategory = product.get('category_2')
            if subcategory:
                category_product_count[subcategory] += 1

        # Implement pagination
        paginator = Paginator(products, 9)
        try:
            paginated_products = paginator.page(page)
        except PageNotAnInteger:
            paginated_products = paginator.page(1)
        except EmptyPage:
            paginated_products = paginator.page(paginator.num_pages)

        # Render the products to the 'shop/products_grid.html' template
        products_grid_html = render_to_string('shop/products_grid.html', {'products': products}, request=self.request)

        # Get products in cart (assuming 'ordered_items_by_shop' is a session variable containing the cart items)
        ordered_items_by_shop = self.request.session.get('ordered_items_by_shop', {})
        products_in_cart = [item['product']['slug'] for shop in ordered_items_by_shop.values() for item in
                            shop['items']]

        # Add the rendered HTML to the context for use in the template
        context['products_grid_html'] = products_grid_html
        context['products'] = paginated_products
        context['sort_option'] = sort_option
        context['products_in_cart'] = products_in_cart
        context['category_product_count'] = dict(category_product_count)

        print(context['category_product_count'])

        return context

    # rating logic
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


class ShopDetailView(ProductDetailView):
    template_name = "shop/shop-single.html"
    context_object_name = 'product'

    # def get(self, request, slug=None, username=None, *args, **kwargs):
    #     if username:
    #         return check_sponsor_and_redirect(request, username, 'shop:single', slug=slug)
    #
    #         # If username is not provided, proceed with the normal GET handling
    #     return super().get(request, slug=slug, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = None
        # Fetch product from API
        product_slug = self.kwargs.get('slug') or self.request.GET.get('slug')

        if not product_slug:
            raise Http404("Product not found")

        product_detail_url = f'https://dashboard.twcako.com/shop/api/get-product/?slug={product_slug}'

        try:
            response = requests.get(product_detail_url)
            response.raise_for_status()  # Raises HTTPError for bad responses
            product_data = response.json()
            product = product_data.get('product', {})
            product_category = product.get('category_1')
            print(f'Product Category: {product_category}')
            print(f'Product Feature: {product.get("feature")}')

            context['product'] = product
        except requests.exceptions.HTTPError as http_err:
            # Log error or notify user
            print(f'HTTP error occurred: {http_err}')
            context['product'] = None
        except requests.exceptions.RequestException as req_err:
            # Log error or notify user
            print(f'Request error occurred: {req_err}')
            context['product'] = None

        # Get related products based on category
        related_products = self.get_related_products(product.get('slug'), product.get('category_1'))

        # # Get products in cart
        # order_ids = self.request.session.get('checkout_orders', [])
        # orders = Order.objects.filter(id__in=order_ids)

        # Get products in cart (assuming 'ordered_items_by_shop' is a session variable containing the cart items)
        ordered_items_by_shop = self.request.session.get('ordered_items_by_shop', {})

        products_in_cart = [item['product']['slug'] for shop in ordered_items_by_shop.values() for item in
                            shop['items']]

        # Check if the user has already purchased the product
        user_has_purchased = False
        if self.request.user.is_authenticated:
            user_has_purchased = OrderItem.objects.filter(order__user=self.request.user, product=product,
                                                          order__complete=True).exists()

        # # Get user rating and review status for the product if authenticated
        # rating = None
        # user_reviewed = False
        # if self.request.user.is_authenticated and user_has_purchased:
        #     try:
        #         rating = Rating.objects.get(product=product, user=self.request.user)
        #         user_reviewed = True
        #     except Rating.DoesNotExist:
        #         rating = None
        #
        # # Get all product ratings
        # product_ratings = Rating.objects.filter(product=product)
        #
        # # Get product reviews
        # product_reviews = product.reviews.select_related('rating').all()
        # for review in product_reviews:
        #     if review.created_at is None:
        #         review.created_at = now()
        #         review.save()

        # Forms

        print(f'Orders by shop: {ordered_items_by_shop}')

        context['rating_form'] = RatingForm()
        context['review_form'] = ReviewForm()

        # Context variables
        context['related_products'] = related_products
        context['products_in_cart'] = products_in_cart
        # context['rating'] = rating
        # context['user_reviewed'] = user_reviewed
        # context['user_has_purchased'] = user_has_purchased
        # context['product_reviews'] = product_reviews
        # context['product_ratings'] = product_ratings

        return context

    def get_related_products(self, current_product_slug, current_category):
        api_url = 'https://dashboard.twcako.com/shop/api/get-product/'

        try:
            # Fetch all products
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()

            if data.get("success"):
                all_products = data.get("products", [])

                # Filter products by the same category and exclude the current product
                related_products = [
                    product for product in all_products
                    if product.get('category_1') == current_category and product.get('slug') != current_product_slug
                ]

                # Shuffle the products randomly
                random.shuffle(related_products)

                # Return only 4 related products
                return related_products[:4]
            else:
                return []
        except requests.exceptions.RequestException as e:
            # Handle API request errors
            print(f'Error fetching products: {str(e)}')
            return []

    # def post(self, request, *args, **kwargs):
    #     self.object = self.get_object()
    #
    #     # Handle Rating Form submission
    #     rating_form = RatingForm(request.POST)
    #     review_form = ReviewForm(request.POST)
    #
    #     if rating_form.is_valid() and review_form.is_valid():
    #         # Ensure a unique rating and review pair
    #         try:
    #             rating = Rating.objects.get(product=self.object, user=request.user)
    #             rating.score = rating_form.cleaned_data['score']
    #             rating.save()
    #         except Rating.DoesNotExist:
    #             rating = rating_form.save(commit=False)
    #             rating.user = request.user
    #             rating.product = self.object
    #             rating.save()
    #
    #         try:
    #             review = Review.objects.get(product=self.object, user=request.user)
    #             review.content = review_form.cleaned_data['content']
    #             review.rating = rating
    #             review.save()
    #         except Review.DoesNotExist:
    #             review = review_form.save(commit=False)
    #             review.user = request.user
    #             review.product = self.object
    #             review.rating = rating
    #             review.save()
    #
    #         return redirect('shop:single', slug=self.object.slug)
    #
    #     # If neither form is valid, render the context with errors
    #     context = self.get_context_data(object=self.object)
    #     context['rating_form'] = rating_form
    #     context['review_form'] = review_form
    #     return self.render_to_response(context)


##################################################
# FOR DASHBOARD

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
                'slug': 'barley-for-cancer',
                'price': 2199,
                'quantity': 2,
                'image': 'img/product/promos/barley/barley-promo-1.png',
                'alt': 'promo 1',
                'name': 'Barley Promo 1',
            },
            {
                'promo': 'promo2',
                'slug': 'barley-for-cancer',
                'price': 2299,
                'quantity': 3,
                'image': 'img/product/promos/barley/barley-promo-1.png',
                'alt': 'promo 2',
                'name': 'Barley Promo 2',
            },
            {
                'promo': 'promo3',
                'slug': 'barley-for-cancer',
                'price': 2840,
                'quantity': 3,
                'image': 'img/product/promos/barley/barley-promo-1.png',
                'alt': 'promo 3',
                'name': 'Barley Promo 3',
            },
            {
                'promo': 'promo4',
                'slug': 'weight-loss',
                'price': 799,
                'quantity': 2,
                'image': 'img/product/promos/barley/barley-promo-1.png',
                'alt': 'promo 4',
                'name': 'Fusion Coffee Promo 1',
            },
            {
                'promo': 'promo5',
                'slug': 'weight-loss',
                'price': 1249,
                'quantity': 5,
                'image': 'img/product/promos/barley/barley-promo-1.png',
                'alt': 'promo 5',
                'name': 'Fusion Coffee Promo 2',
            },
            {
                'promo': 'promo6',
                'slug': 'weight-loss',
                'price': 1649,
                'quantity': 7,
                'image': 'img/product/promos/barley/barley-promo-1.png',
                'alt': 'promo 6',
                'name': 'Fusion Coffee Promo 3',
            },
            {
                'promo': 'promo7',
                'sku': 'boost-coffee',
                'price': 899,
                'quantity': 2,
                'image': 'img/product/promos/barley/barley-promo-1.png',
                'alt': 'promo 7',
                'name': 'Boost Coffee Promo 1',
            },
            {
                'promo': 'promo8',
                'slug': 'boost-coffee',
                'price': 1349,
                'quantity': 5,
                'image': 'img/product/promos/barley/barley-promo-1.png',
                'alt': 'promo 8',
                'name': 'Boost Coffee Promo 2',
            },
            {
                'promo': 'promo9',
                'slug': 'boost-coffee',
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
