from django.db.models import Avg
from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, Http404
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from collections import defaultdict

from onlinestore.utils import check_sponsor_and_redirect
from onlinestore.models import *

import requests
import random

User = get_user_model()


class ShopView(TemplateView):
    template_name = 'shop/shop.html'
    context_object_name = 'products'
    paginate_by = 9
    _product_choices = None
    title = "Shop"

    def get(self, request, username=None, *args, **kwargs):

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            products, category_product_count, has_next = self.get_paginated_queryset()
            ordered_items_by_shop = self.request.session.get('ordered_items_by_shop', {})
            products_in_cart = [item['product']['slug'] for shop in ordered_items_by_shop.values() for item in
                                shop['items']]
            products_grid_html = render_to_string('shop/products_grid.html', {'products': products}, request=request)

            return JsonResponse({
                'products_grid_html': products_grid_html,
                'products': products,
                'products_in_cart': products_in_cart,
                'category_product_count': category_product_count,
                'has_next': has_next

            })

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        category_id = self.request.GET.get('category_id')
        search_query = self.request.GET.get('q')
        sort_option = self.request.GET.get('sort', '1')
        queryset = []
        full_product_list = []
        category_product_count = defaultdict(int)

        api_url = 'https://dashboard.twcako.com/shop/api/get-product/'

        try:
            # Make the API request
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()

            if data.get("success"):
                full_product_list = data.get("products", [])

                # Count products in each category before filtering
                for product in full_product_list:
                    category_1 = product.get('category_1')
                    category_2 = product.get('category_2')

                    if category_1 and category_1.lower() != 'twc':  # Exclude 'twc' products
                        category_product_count[category_1] += 1
                    if category_2 and category_2.lower() != 'twc':  # Exclude 'twc' products
                        category_product_count[category_2] += 1

                # Start with the unfiltered list for further processing
                queryset = full_product_list

                queryset = [
                    product for product in queryset
                    if product.get('category_1', '').lower() != 'twc'
                ]

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

                # Apply offset and limit for lazy loading
                print(f'Products: {queryset}')

                # Count products in each category
                for product in queryset:
                    # Fetch all ratings for this product from the Rating model
                    product_slug = product.get('slug')
                    ratings = Rating.objects.filter(product_slug=product_slug)
                    if ratings.exists():
                        aggregate_rating = ratings.aggregate(Avg('score'))['score__avg']
                        product['aggregate_rating'] = round(aggregate_rating, 1)
                    else:
                        product['aggregate_rating'] = 3

            return queryset, dict(category_product_count)

        except requests.exceptions.RequestException as e:
            # Handle API request errors by returning empty queryset and product count
            return [], {}

    def get_paginated_queryset(self):
        """
        This method paginates the queryset manually since the API returns all products.
        """
        products, category_product_count = self.get_queryset()
        page = int(self.request.GET.get('page', 1))  # Default to page 1
        paginate_by = self.paginate_by

        # Calculate start and end indices for pagination
        start = (page - 1) * paginate_by
        end = start + paginate_by

        # Slice the products list for pagination
        paginated_products = products[start:end]
        has_next = len(products) > end  # Check if more products are available
        print(f'Has Next: {has_next}')

        return paginated_products, category_product_count, has_next

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sort_option = self.request.GET.get('sort', '1')

        # Fetch the products from the API using the get_queryset method
        products, category_product_count, _ = self.get_paginated_queryset()
        user_ratings = self.get_user_ratings(products)

        category_id = self.request.GET.get('category_id', 'all')


        # Render the products to the 'shop/products_grid.html' template
        products_grid_html = render_to_string('shop/products_grid.html', {'products': products}, request=self.request)

        # Get products in cart (assuming 'ordered_items_by_shop' is a session variable containing the cart items)
        ordered_items_by_shop = self.request.session.get('ordered_items_by_shop', {})
        products_in_cart = [item['product']['slug'] for shop in ordered_items_by_shop.values() for item in shop['items']]

        context['products_grid_html'] = products_grid_html
        context['category_id'] = category_id
        context['products'] = products
        context['sort_option'] = sort_option
        context['products_in_cart'] = products_in_cart
        context['category_product_count'] = category_product_count
        context['user_ratings'] = user_ratings

        return context

    # Modified rating logic to work with product_slug
    def get_user_ratings(self, products):
        user_ratings = {}
        if self.request.user.is_authenticated:
            for product in products:
                product_slug = product.get('slug')
                user_ratings[product_slug] = None
                try:
                    rating = Rating.objects.get(product_slug=product_slug, user=self.request.user)
                    user_ratings[product_slug] = rating.score
                except Rating.DoesNotExist:
                    pass
        return user_ratings


class ShopDetailView(View):
    template_name = "shop/shop-single.html"

    def get(self, request, slug):
        product = None
        # Fetch product from API
        product_slug = slug or request.GET.get('slug')

        if not product_slug:
            raise Http404("Product not found")

        product_detail_url = f'https://dashboard.twcako.com/shop/api/get-product/?slug={product_slug}'

        try:
            response = requests.get(product_detail_url, verify=False)
            response.raise_for_status()  # Raises HTTPError for bad responses
            product_data = response.json()
            product = product_data.get('product', {})
            if not product:
                raise Http404("Product not found")

        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise Http404("Product not found")

        except requests.exceptions.RequestException as req_err:
            print(f'Request error occurred: {req_err}')
            return render(request, self.template_name, {'product': None})

            # Get the product rating
        product_slug = product.get('slug')
        ratings = Rating.objects.filter(product_slug=product_slug)

        if ratings.exists():
            aggregate_rating = ratings.aggregate(Avg('score'))['score__avg']
            product['aggregate_rating'] = round(aggregate_rating, 1)
        else:
            product['aggregate_rating'] = 3  # Default rating if no ratings exist

        # Get related products based on category
        related_products = self.get_related_products(product.get('slug'), product.get('category_1'))


        # Get products in cart (assuming 'ordered_items_by_shop' is a session variable containing the cart items)
        ordered_items_by_shop = request.session.get('ordered_items_by_shop', {})
        products_in_cart = [item['product']['slug'] for shop in ordered_items_by_shop.values() for item in shop['items']]

        context = {
            'product': product,
            'related_products': related_products,
            'products_in_cart': products_in_cart,
        }

        return render(request, self.template_name, context)

    def get_related_products(self, current_product_slug, current_category):
        api_url = 'https://dashboard.twcako.com/shop/api/get-product/'

        try:
            # Fetch all products
            response = requests.get(api_url, verify=False)
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

# @login_required
# def get_review_details(request, review_id):
#     review = get_object_or_404(Review, id=review_id, user=request.user)
#     rating = Rating.objects.get(review=review)
#     return JsonResponse({'content': review.content, 'rating': rating.score})


# @login_required
# @require_POST
# def edit_review(request, review_id):
#     try:
#         print(f"Request Method: {request.method}")
#         print(f"Review ID: {review_id}")
#
#         review = get_object_or_404(Review, id=review_id, user=request.user)
#         print(f"Review found: {review}")
#
#         # Update the review content
#         review.content = request.POST.get('content')
#         review.save()
#
#         # Update the rating
#         rating = review.rating
#         rating.score = request.POST.get('rating')
#         rating.save()
#
#         print("Form is valid and saved")
#         return JsonResponse({'success': True, 'message': 'Review updated successfully!'})
#     except Exception as e:
#         print(f"Exception: {e}")
#         return JsonResponse({'success': False, 'message': str(e)})


