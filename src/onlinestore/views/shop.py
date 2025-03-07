import os

import requests
import random

from allauth.socialaccount.providers.mediawiki.provider import settings
from django.conf import settings
from django.db.models import Avg
from django.shortcuts import render
from django.template.defaultfilters import title
from django.views.generic import TemplateView, View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, Http404
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from collections import defaultdict
from onlinestore.utils import check_sponsor_and_redirect
from onlinestore.models import *


User = get_user_model()


class ShopView(TemplateView):
    template_name = 'shop/shop.html'
    context_object_name = 'products'
    paginate_by = 9

    def get(self, request, username=None, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            products, category_product_count, has_next = self.get_paginated_queryset()
            ordered_items_by_shop = self.request.session.get('ordered_items_by_shop', {})
            products_in_cart = [item['product']['slug'] for shop in ordered_items_by_shop.values() for item in
                                shop['items']]
            products_grid_html = render_to_string('shop/products_grid.html', {'products': products, 'excluded_suppliers': ['sante', 'promos', 'twc']}, request=request)

            return JsonResponse({
                'products_grid_html': products_grid_html,
                'products': products,
                'products_in_cart': products_in_cart,
                'category_product_count': category_product_count,
                'has_next': has_next,
                'excluded_suppliers': ['sante', 'promos', 'twc'],
            })

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        cat1 = self.request.GET.get('cat1')
        cat2 = self.request.GET.get('cat2')
        search_query = self.request.GET.get('q')
        sort_option = self.request.GET.get('sort', '1')

        # ✅ Fix: Use a nested defaultdict for category counts
        category_product_count = defaultdict(lambda: defaultdict(int))

        # Build API request URL with filters
        api_url = settings.SHOP_PRODUCTS_API
        params = {}

        if cat1:
            params['cat1'] = cat1
        if cat2:
            params['cat2'] = cat2

        try:
            # Fetch filtered data from API
            response = requests.get(api_url, params=params)
            response.raise_for_status()
            data = response.json()

            if not data.get("success"):
                return [], {}

            queryset = [product for product in data.get("products", []) if not product.get("is_for_vw", False)]

            # ✅ Count products per category
            for product in queryset:
                category_1 = product.get('category_1', '').strip().lower()
                category_2 = product.get('category_2', '').strip().lower()

                if category_1:
                    category_product_count[category_1]["_count"] += 1  # Total count for cat1
                if category_1 and category_2:
                    category_product_count[category_1][category_2] += 1  # Count for cat2 under cat1


            # Apply search filter (optional)
            if search_query:
                queryset = [
                    product for product in queryset
                    if search_query.lower() in product.get('name', '').lower()
                       or search_query.lower() in product.get('category_1', '').lower()
                       or search_query.lower() in product.get('category_2', '').lower()
                ]

            # Apply sorting
            if sort_option == '5':  # Latest Items
                queryset = sorted(queryset, key=lambda p: p.get('timestamp', ''), reverse=True)
            elif sort_option == '3':  # Price - Low To High
                queryset = sorted(queryset, key=lambda p: p.get('customer_price', 0))
            elif sort_option == '4':  # Price - High To Low
                queryset = sorted(queryset, key=lambda p: p.get('customer_price', 0), reverse=True)

            # Aggregate ratings
            for product in queryset:
                product_slug = product.get('slug')
                # ratings = Rating.objects.filter(product_slug=product_slug)
                # aggregate_rating = ratings.aggregate(Avg('score'))['score__avg'] if ratings.exists() else 5
                aggregate_rating = 5
                product['aggregate_rating'] = round(aggregate_rating, 1)

            return queryset, dict(category_product_count)  # Convert defaultdict to normal dict

        except requests.exceptions.RequestException:
            return [], {}

    def get_paginated_queryset(self):
        """
        Paginate the queryset manually.
        """
        products, category_product_count = self.get_queryset()
        page = int(self.request.GET.get('page', 1))
        paginate_by = self.paginate_by

        start = (page - 1) * paginate_by
        end = start + paginate_by

        paginated_products = products[start:end]
        has_next = len(products) > end

        return paginated_products, category_product_count, has_next

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sort_option = self.request.GET.get('sort', '1')
        cat1 = self.request.GET.get('cat1', 'all')
        cat2 = self.request.GET.get('cat2')

        products, category_product_count, _ = self.get_paginated_queryset()
        # user_ratings = self.get_user_ratings(products)
        user_ratings = 5

        if cat1 and cat1.lower() != 'all':
            context['title'] = cat1.title()
        else:
            context['title'] = "Shop"

        products_grid_html = render_to_string('shop/products_grid.html', {'products': products}, request=self.request)

        ordered_items_by_shop = self.request.session.get('ordered_items_by_shop', {})
        products_in_cart = [item['product']['slug'] for shop in ordered_items_by_shop.values() for item in
                            shop['items']]

        categories = [
            "sante-nutraceutical", "sante-beverage", "sante-intimate_care",
            "bath-body", "bags", "watches", "electronics", "perfume", "accessories"
        ]

        category_labels = {
            "sante-nutraceutical": "Health & Wellness",
            "sante-beverage": "Healthy Beverages",
            "sante-intimate_care": "Intimate Care",
            "bath-body": "Bath & Body",
            "bags": "Bags",
            "watches": "Watches",
            "electronics": "Electronics",
            "perfume": "Perfumes",
            "accessories": "Accessories",
        }

        formatted_categories = [cat.replace("-", " ").title() for cat in categories]

        context.update({
            'products_grid_html': products_grid_html,
            'cat1': cat1,
            'cat2': cat2,
            'products': products,
            'sort_option': sort_option,
            'products_in_cart': products_in_cart,
            'category_product_count': category_product_count,
            'user_ratings': user_ratings,
            'excluded_suppliers': ['sante', 'promos', 'twc'],
            "categories": zip(categories, formatted_categories),
            'category_labels': category_labels,  # Add category_labels here
        })

        return context

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

        HOST_DOMAIN = os.environ.get("HOST_DOMAIN", "twcako")
        product_detail_url = f'https://dashboard.{HOST_DOMAIN}.com/shop/api/get-product/?slug={product_slug}'

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
            product['aggregate_rating'] = 5  # Default rating if no ratings exist

        # Get related products based on category
        related_products = self.get_related_products(product.get('slug'), product.get('category_1'))


        # Get products in cart (assuming 'ordered_items_by_shop' is a session variable containing the cart items)
        ordered_items_by_shop = request.session.get('ordered_items_by_shop', {})
        products_in_cart = [item['product']['slug'] for shop in ordered_items_by_shop.values() for item in
                            shop['items']]

        context = {
            'product': product,
            'related_products': related_products,
            'products_in_cart': products_in_cart,
            'title': product['name'],
            'excluded_suppliers': ['sante', 'promos', 'twc']
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

                # Filter out the current product and VW products
                related_products = [
                    product for product in all_products
                    if product.get('category_1') == current_category
                       and product.get('slug') != current_product_slug
                       and not product.get('is_for_vw', False)  # Exclude VW products
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
