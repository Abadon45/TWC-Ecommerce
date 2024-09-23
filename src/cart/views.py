from django.utils import timezone
from decimal import Decimal

from django.shortcuts import redirect, get_object_or_404
from django.http import Http404
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

from .models import *
from onlinestore.forms import AddressForm
from onlinestore.models import *
from onlinestore.utils import send_temporary_account_email
from .utils import sf_calculator

import requests
import decimal

User = get_user_model()


class CartView(TemplateView):
    template_name = 'cart/shop-cart.html'
    title = "Cart"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Retrieve ordered_items_by_shop and total_cart_subtotal from the session
        ordered_items_by_shop = self.request.session.get('ordered_items_by_shop', {})

        # Log the structure of each product's slug
        for shop, data in ordered_items_by_shop.items():
            for item in data['items']:
                print(f"Product name: {item['product']['name']}, Slug: {item['product'].get('slug', 'No slug')}")

        # Update the context with data retrieved from the session
        context.update({
            'title': self.title,
            'ordered_items_by_shop': ordered_items_by_shop,
        })

        return context

class UpdateCartView(View):
    def get_product_data(self, product_slug):
        """Fetch product data from the API."""
        product_url = f'https://dashboard.twcako.com/shop/api/get-product/?slug={product_slug}'
        try:
            response = requests.get(product_url, verify=False)
            response.raise_for_status()
            data = response.json()

            if data['success']:
                return data['product']
            else:
                return None
        except requests.RequestException as e:
            print(f"Error fetching product data: {e}")
            return None

    def update_cart(self, request, product_slug, action, quantity):
        """Update the cart stored in the session."""
        # Fetch product data from the API
        product = self.get_product_data(product_slug)
        MAX_ORDER_QUANTITY = int(SiteSetting.get_max_order_quantity())
        max_order_exceeded = False
        message = "Cart updated"

        order_complete = False
        self.request.session['order_complete'] = order_complete


        print(f'max_order_quantity: {MAX_ORDER_QUANTITY}')

        if not product:
            return None, 'Product not found or API error'

        # Retrieve the cart from the session, or create an empty one
        cart = request.session.get('cart', {})

        # Get the shop (category_1) for grouping
        shop = product.get('category_1', 'Unknown Shop')

        # Get the item from the cart or initialize it
        item = cart.get(product_slug, {
            'id': product['sku'],
            'name': product['name'],
            'shop': shop,
            'slug': product_slug,
            'image': product.get('image_1', None),
            'quantity': 0,
            'price': product['customer_price'],
        })

        # Calculate the current total quantity for the shop
        shop_total_quantity = sum(
            cart_item['quantity'] for slug, cart_item in cart.items() if cart_item['shop'] == shop
        )

        # Update item quantity based on action
        if action == 'add':
            if shop_total_quantity + quantity > MAX_ORDER_QUANTITY:
                max_order_exceeded = True
                message = f"Cannot add more than {MAX_ORDER_QUANTITY} items per order."
            else:
                item['quantity'] += quantity
        elif action == 'minus':
            item['quantity'] -= quantity
        elif action == 'remove':
            # Remove the item from the cart
            cart.pop(product_slug, None)
            request.session['cart'] = cart
            request.session.modified = True

            # Rebuild ordered_items_by_shop after removing the item
            ordered_items_by_shop = self._rebuild_ordered_items_by_shop(cart)

            # Save ordered_items_by_shop in session
            request.session['ordered_items_by_shop'] = ordered_items_by_shop
            request.session.modified = True

            return cart, 'Item removed', ordered_items_by_shop, max_order_exceeded

        # Ensure the quantity doesn't go below 0
        if item['quantity'] <= 0:
            cart.pop(product_slug, None)
        else:
            cart[product_slug] = item


        # Update the session with the new cart
        request.session['cart'] = cart
        request.session.modified = True

        # Rebuild ordered_items_by_shop from the updated cart
        ordered_items_by_shop = self._rebuild_ordered_items_by_shop(cart)

        # Save ordered_items_by_shop in session
        request.session['ordered_items_by_shop'] = ordered_items_by_shop
        request.session.modified = True

        print(f'Orders CART: {cart}')
        print(f'Orders SHOP: {ordered_items_by_shop}')
        # print(f'Order subtotal: {}')
        print(f'max_order_exceeded: {max_order_exceeded}')

        return cart, message, ordered_items_by_shop, max_order_exceeded

    def _rebuild_ordered_items_by_shop(self, cart):
        """Helper method to rebuild ordered_items_by_shop from the cart."""
        ordered_items_by_shop = {}

        for slug, cart_item in cart.items():
            shop = cart_item['shop']
            if shop not in ordered_items_by_shop:
                ordered_items_by_shop[shop] = {'items': [], 'subtotal': 0}

            ordered_items_by_shop[shop]['items'].append({
                'product': cart_item,
                'quantity': cart_item['quantity'],
                'get_total': float(cart_item['price']) * cart_item['quantity'],
            })

        # Calculate and update subtotal for each shop
        for shop, data in ordered_items_by_shop.items():
            items = data['items']
            subtotal = sum(item['get_total'] for item in items)
            ordered_items_by_shop[shop]['subtotal'] = subtotal

        return ordered_items_by_shop

    def get(self, request, *args, **kwargs):
        """Handle GET requests to update the cart."""
        product_slug = request.GET.get('productId')
        action = request.GET.get('action')
        quantity = int(request.GET.get('quantity', 1))

        # Print the received data for debugging
        print(f"Received GET data - Product Slug: {product_slug}, Action: {action}, Quantity: {quantity}")

        if not product_slug or not action:
            return JsonResponse({'error': 'Invalid request'}, status=400)

        # Update the cart
        cart, message, ordered_items_by_shop, max_order_exceeded = self.update_cart(request, product_slug, action, quantity)

        if cart is None:
            return JsonResponse({
                'error': True,
                'message': message
            }, status=400)

        # Calculate total items in cart
        total_items = sum(item['quantity'] for item in cart.values())
        total_price = sum(float(item['price']) * item['quantity'] for item in cart.values())

        # Add get_total for each item in the cart response
        for item in cart.values():
            item['get_total'] = float(item['price']) * item['quantity']


        # Return a response
        return JsonResponse({
            'error': False,
            'message': message,
            'cart_items': total_items,
            'total_cart_price': total_price,
            'cart': cart,
            'shop_cart':ordered_items_by_shop,
            'max_order_exceeded': max_order_exceeded,
        }, status=200)


class CheckoutView(FormView):
    template_name = 'cart/shop-checkout.html'
    form_class = AddressForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orders = self.get_orders()
        referred_by = self.request.session.get('referrer')

        print(f'Sponsor: {referred_by}')
        context.update({
            'orders': orders,
            'shipping_form': self.get_form(),
            'referred_by': referred_by,
        })
        return context

    def calculate_shipping_fee(self, region, order):
        """
        Calculate the shipping fee based on the region and order quantity.
        """
        FIXED_SHIPPING_FEE = SiteSetting.get_fixed_shipping_fee()

        if FIXED_SHIPPING_FEE > 0:
            return FIXED_SHIPPING_FEE
        else:
            qty = order['quantity']
            return sf_calculator(region=region, qty=qty)

    @csrf_exempt
    def form_valid(self, form):
        print("Request Headers:", self.request.headers)
        print("Request Method:", self.request.method)
        print("Request Path:", self.request.path)
        shipping_address = form.save(commit=False)
        region = form.cleaned_data.get('region')

        # Save the address to session
        self.request.session['shipping_address'] = {
            'first_name': shipping_address.first_name,
            'last_name': shipping_address.last_name,
            'phone': shipping_address.phone,
            'line1': shipping_address.line1,
            'province': shipping_address.province,
            'city': shipping_address.city,
            'barangay': shipping_address.barangay,
            'postcode': shipping_address.postcode,
        }

        address_from_session = self.request.session.get('shipping_address', {})
        print(f"Address: {address_from_session}")

        orders = self.get_orders()
        updated_orders = []
        total_shipping = 0
        total_payment = 0

        # Calculate shipping fees and update orders
        for shop, order_data in orders.items():
            if isinstance(order_data, dict) and 'subtotal' in order_data:
                qty = sum(item['quantity'] for item in order_data['items'])
                shipping_fee = Decimal(self.calculate_shipping_fee(region, {'shop': shop, 'qty': qty}))
                total_shipping += decimal.Decimal(shipping_fee)
                subtotal = Decimal(order_data['subtotal'])
                total_amount = subtotal + shipping_fee
                total_payment += total_amount
                updated_orders.append({
                    'shop': shop,
                    'shipping_fee': float(shipping_fee),
                    'total_amount': float(total_amount),
                })
            else:
                print("Unexpected order format:", order_data)

        self.request.session['updated_orders'] = updated_orders

        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            response_data = {
                'status': 'success',
                'updated_orders': updated_orders,
                'total_shipping': str(total_shipping),
                'total_payment': str(total_payment),
            }
            return JsonResponse(response_data)
        else:
            return redirect(self.success_url)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            print("Form Errors:", form.errors)
            return JsonResponse({'status': 'error', 'errors': form.errors})
        return self.render_to_response(self.get_context_data(form=form))

    def get_orders(self):
        ordered_items_by_shop = self.request.session.get('ordered_items_by_shop', {})
        return ordered_items_by_shop



#########################################################
#----------Change address from list of addresses--------#
#########################################################

def get_selected_address(request):
    # Log the incoming GET request to 'get-selected-address'
    print("Incoming GET request to 'get-selected-address'")

    # Ensure that the request method is GET; return an error response if not
    if request.method != 'GET':
        return JsonResponse({'success': False, 'error': 'Invalid request method.'})

    # Retrieve the selected address ID from the GET parameters
    selected_address_id = request.GET.get('selected_address_id')
    print(f"selected address: {selected_address_id}")

    # If the selected address ID is missing, return an error response
    if not selected_address_id:
        return JsonResponse({'success': False, 'error': 'Missing address ID.'})

    try:
        # Attempt to retrieve the selected address from the database
        selected_address = get_object_or_404(Address, pk=selected_address_id)
        print(selected_address.barangay)
    except Http404:
        # If the address is not found, return an error response
        return JsonResponse({'success': False, 'error': 'Address not found.'})

    try:
        # Get the current user and their incomplete orders
        user = request.user

    except Exception as e:
        # Handle any exceptions during the update process and return an error response
        print(f"Exception in checkout view: {e}")
        return JsonResponse({'error': 'Internal Server Error'}, status=500)

    # Prepare the selected address data to be returned in the JSON response
    address_data = {
        'first_name': selected_address.first_name,
        'last_name': selected_address.last_name,
        'email': selected_address.email,
        'phone': selected_address.phone,
        'region': selected_address.region,
        'province': selected_address.province,
        'city': selected_address.city,
        'barangay': selected_address.barangay,
        'line1': selected_address.line1,
        'line2': selected_address.line2,
        'postcode': selected_address.postcode,
        'message': selected_address.message,
        'is_default': selected_address.is_default,
    }

    # Return a success response with the selected address data
    return JsonResponse({'success': True, 'address': address_data})

#########################################################
#-------Edit an address from the list of addresses------#
#########################################################

def edit_checkout_address(request):
    if request.method == 'POST':
        address_id = request.POST.get('address_id')

        new_data = {
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'email': request.POST.get('email'),
            'phone': request.POST.get('phone'),
            'region': request.POST.get('region'),
            'province': request.POST.get('province'),
            'city': request.POST.get('city'),
            'barangay': request.POST.get('barangay'),
            'line1': request.POST.get('line1'),
            'line2': request.POST.get('line2'),
            'postcode': request.POST.get('postcode'),
            'message': request.POST.get('message'),
        }

        print("Address ID:", address_id)
        print("New Data:", new_data)

        # Update the address
        try:
            address = Address.objects.get(pk=address_id)
            print("Existing Address:", address)

            for key, value in new_data.items():
                setattr(address, key, value)
            address.save()
            print("Address Updated Successfully")
            return JsonResponse({'success': True, 'address_id': address_id, 'new_data': new_data})
        except Address.DoesNotExist:
            print("Address not found")
            return JsonResponse({'success': False, 'error': 'Address not found'})
    else:
        print("Invalid request method")
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

def get_checkout_address_details(request):
    if request.method == 'GET':
        address_id = request.GET.get('address_id')
        try:
            address = Address.objects.get(pk=address_id)

            address_data = {
                'address_id': address_id,
                'first_name': address.first_name,
                'last_name': address.last_name,
                'email': address.email,
                'phone': address.phone,
                'region': address.region,
                'province': address.province,
                'city': address.city,
                'barangay': address.barangay,
                'line1': address.line1,
                'line2': address.line2,
                'postcode': address.postcode,
                'message': address.message,
            }
            return JsonResponse({'success': True, 'address': address_data})
        except Address.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Address not found'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})


#########################
# Set Order to Complete #
#########################

def submit_checkout(request):


    # If the request method is POST, handle the form submission
    if request.method == 'POST':
        # Get the referrer's username from the POST data
        ordered_items_by_shop = request.session.get('ordered_items_by_shop', {})

        # Prepare the payload with only the products and quantities
        order_payload = []
        for shop, shop_data in ordered_items_by_shop.items():
            for item in shop_data['items']:
                print(item['product'])
                order_payload.append({
                    'sku': item['product']['id'],
                    'quantity': item['quantity'],
                })

        print(f'Order payload: {order_payload}')

        referrer_username = request.POST.get('username')


        if referrer_username:
            # API URL to check if the referrer username exists in the system
            api_url = f'https://dashboard.twcako.com/account/api/check-username/{referrer_username}/'


            try:
                if referrer_username != 'admin':
                    # Make an API request to validate the referrer username
                    response = requests.get(api_url, verify=False)
                    response.raise_for_status()  # Raise an error for bad HTTP status codes
                    data = response.json()

                    # Ensure the API response is a valid JSON object
                    if not isinstance(data, dict):
                        raise ValueError("API response is not a valid JSON object")

                    # Check if the API response indicates success
                    is_success = data.get('success')
                    order_complete = True
                    request.session['order_complete'] = order_complete
                    request.session['referrer'] = referrer_username
                    request.session.modified = True

                    # If the username doesn't exist, return an error response
                    if not is_success:
                        return JsonResponse({'success': False, 'error': 'Referrer username does not exist'}, status=400)

            except requests.RequestException as e:
                # Handle request exceptions (e.g., network issues, server errors)
                print(f"Request failed: {e}")
                return JsonResponse({'success': False, 'error': 'Failed to check referrer username'}, status=500)
            except ValueError as e:
                # Handle JSON parsing errors
                print(f"Error parsing response: {e}")
                return JsonResponse({'success': False, 'error': 'Invalid API response'}, status=500)

        '''DELETE THIS AFTER API IS FINISHED'''
        return redirect('cart:checkout_complete')

        # Send the payload to the API
        # try:
        #     response = requests.post(order_api_url, json={'products': order_payload})
        #     response.raise_for_status()
        #     api_response = response.json()
        #
        #     if api_response.get('success'):
        #         # Set order_complete to True
        #         request.session['order_complete'] = True
        #         request.session.modified = True
        #
        #         # Copy the current ordered_items_by_shop for future reference
        #         completed_order = ordered_items_by_shop.copy()
        #
        #         # Clear cart and ordered_items_by_shop from session
        #         request.session.pop('cart', None)
        #         request.session.pop('ordered_items_by_shop', None)
        #         request.session.modified = True
        #
        #         # Save the completed order for future reference (optional, can store elsewhere)
        #         request.session['completed_order'] = completed_order
        #         request.session.modified = True
        #
        #         return redirect('cart:checkout_complete')
        #
        #     else:
        #         return JsonResponse({'success': False, 'error': 'Order submission failed'}, status=400)
        #
        # except requests.RequestException as e:
        #     print(f"API request failed: {e}")
        #     return JsonResponse({'success': False, 'error': 'Failed to submit order'}, status=500)


    return redirect('cart:cart')


#########################################################
#------------------checkout is done---------------------#
#########################################################


class CheckoutDoneView(TemplateView):
    template_name = 'cart/shop-checkout-complete.html'
    title = "Checkout Done"

    def get(self, request, *args, **kwargs):
        # Check if 'order_complete' exists in the session
        order_complete = self.request.session.get('order_complete', False)

        # Redirect to home if the order is not complete
        if not order_complete:
            return redirect("home_view")

        # Otherwise, proceed with rendering the template
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)


        total_payment = 0.0
        current_date = timezone.now().strftime('%b %d, %Y')

        # Retrieve ordered_items_by_shop and total_cart_subtotal from the session
        if 'ordered_items_by_shop' in self.request.session:
            ordered_items_by_shop = self.request.session.get('ordered_items_by_shop', {})
            orders = ordered_items_by_shop.copy()

            self.request.session.pop('cart', None)
            self.request.session.pop('ordered_items_by_shop', None)

            self.request.session['orders'] = orders
        else:
            orders = self.request.session.get('orders', [])

        checkout_details = self.request.session.get('updated_orders', {})
        address_from_session = self.request.session.get('shipping_address', {})
        print(f'Referrer saved: {self.request.session.get("referrer")}')


        # Process checkout_details to create a lookup dictionary for easy access
        checkout_details_dict = {detail['shop']: detail for detail in checkout_details}

        # Add extra information to ordered_items_by_shop
        for shop, shop_data in orders.items():
            shop_detail = checkout_details_dict.get(shop, {})
            # Calculate total_quantity for the shop
            total_quantity = sum(item['quantity'] for item in shop_data['items'])
            shop_data['total_quantity'] = total_quantity

            shop_data['shipping_fee'] = shop_detail.get('shipping_fee', 0)
            shop_data['total_amount'] = shop_detail.get('total_amount', 0)

            total_payment += float(shop_detail.get('total_amount', 0))

        print(f'Orders: {orders}')
        print(f'Address: {address_from_session}')

        # Update the context with data retrieved from the session
        context.update({
            'title': self.title,
            'orders': orders,
            'checkout_details': checkout_details,
            'address': address_from_session,
            'total_payment': total_payment,
            'current_date': current_date,
            'sponsor': self.request.session.get('referrer', 'No referrer set'),
        })

        return context


def set_order_id_session_variable(request):
    if request.method == 'POST' and request.is_ajax():
        order_id = request.POST.get('order_id')
        request.session['clicked_order_id'] = order_id
        print(f'Order ID: {order_id}')
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})
