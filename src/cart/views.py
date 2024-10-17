from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
from django.shortcuts import redirect, get_object_or_404, render
from django.http import Http404
from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse
from urllib.parse import urlencode

from onlinestore.forms import AddressForm
from onlinestore.models import *
from .utils import *
# from TWC.settings.base import *
from django.core.mail import send_mail

import requests
import decimal
import json

User = get_user_model()


class CartView(TemplateView):
    template_name = 'cart/shop-cart.html'
    title = "Cart"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Retrieve ordered_items_by_shop and total_cart_subtotal from the session
        ordered_items_by_shop = self.request.session.get('ordered_items_by_shop', {})
        cart_total = 0

        # Log the structure of each product's slug
        for shop, data in ordered_items_by_shop.items():
            cod_amount = data.get('cod_amount', 0)
            cart_total += cod_amount

        self.request.session['cart_total'] = cart_total
        # Update the context with data retrieved from the session
        context.update({
            'title': self.title,
            'ordered_items_by_shop': ordered_items_by_shop,
            'cart_total': cart_total,
        })

        return context


class UpdateCartView(View):
    def get_product_data(self, product_slug):
        """Fetch product data from the API."""
        product_url = f'https://dashboard.twcako.com/shop/api/get-product/?slug={product_slug}'
        try:
            response = requests.get(product_url)
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
            "barley_point": product['barley_point'],
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
        FIXED_SHIPPING_FEE = SiteSetting.get_fixed_shipping_fee()
        discount = 0.00

        for slug, cart_item in cart.items():
            shop = cart_item['shop']
            if shop not in ordered_items_by_shop:
                ordered_items_by_shop[shop] = {
                    'items': [],
                    'total_quantity':0,
                    'subtotal': 0,
                    'shipping_fee':0,
                    'discount':0,
                    'cod_amount': 0,
                }

            ordered_items_by_shop[shop]['items'].append({
                'product': {
                    'id': cart_item['id'],
                    'name': cart_item['name'],
                    'shop': cart_item['shop'],
                    'slug': cart_item['slug'],
                    'image': cart_item['image'],
                    'price': cart_item['price'],
                    "barley_point": cart_item['barley_point'],
                },
                'quantity': cart_item['quantity'],
                'get_total': float(Decimal(cart_item['price']) * cart_item['quantity']),
            })

        # Calculate and update subtotal and cod amount for each shop
        for shop, data in ordered_items_by_shop.items():
            items = data['items']
            total_quantity = sum(item['quantity'] for item in items)
            ordered_items_by_shop[shop]['total_quantity'] = total_quantity
            subtotal = sum(float(item['get_total']) for item in items)
            ordered_items_by_shop[shop]['subtotal'] = subtotal
            ordered_items_by_shop[shop]['discount'] = float(discount)
            cod_amount = subtotal + float(FIXED_SHIPPING_FEE) - float(discount)
            ordered_items_by_shop[shop]['cod_amount'] = cod_amount

        return ordered_items_by_shop

    def get(self, request, *args, **kwargs):
        """Handle GET requests to update the cart."""
        # Extract bundleDetails from the request (assuming it's sent as JSON)
        bundle_details = request.GET.get('bundleDetails')

        # Parse the bundleDetails from JSON (if it was sent in JSON format)
        try:
            bundle_details = json.loads(bundle_details) if bundle_details else {}
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid bundleDetails format'}, status=400)

        """Handle GET requests to update the cart."""
        product_slug = request.GET.get('productId')
        action = request.GET.get('action')
        quantity = int(request.GET.get('quantity', 1))

        FIXED_SHIPPING_FEE = SiteSetting.get_fixed_shipping_fee()
        total_price = Decimal('0.00')

        # Print the received data for debugging
        print(f"Received GET data - Product Slug: {product_slug}, Action: {action}, Quantity: {quantity}")

        if not product_slug or not action:
            return JsonResponse({'error': 'Invalid request'}, status=400)

        # Update the cart
        cart, message, ordered_items_by_shop, max_order_exceeded = self.update_cart(request, product_slug, action,
                                                                                    quantity)

        if cart is None:
            return JsonResponse({
                'error': True,
                'message': message
            }, status=400)

        # Calculate total items in cart
        total_items = sum(item['quantity'] for item in cart.values())
        for shop, data in ordered_items_by_shop.items():
            items = data['items']
            subtotal = sum(Decimal(item['get_total']) for item in items)
            total_amount = subtotal + Decimal(FIXED_SHIPPING_FEE)
            total_price += total_amount


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
            'shop_cart': ordered_items_by_shop,
            'max_order_exceeded': max_order_exceeded,
        }, status=200)


class CheckoutView(View):
    template_name = 'cart/shop-checkout.html'

    def get_context_data(self, **kwargs):
        context = {
            'shipping_form': AddressForm(),
            'orders': self.get_orders(),
            'cart_total': self.request.session.get('cart_total', 0),
            'referred_by': self.request.session.get('referrer'),
        }
        return context

    def get(self, request, *args, **kwargs):
        orders = self.get_orders()
        if not orders:
            return redirect('shop:shop')

        if 'first_name' in request.GET:  # Check if the form was submitted
            return self.process_shipping_info(request.GET)

        context = self.get_context_data()
        return render(request, self.template_name, context)

    def process_shipping_info(self, data):

        payment_method = data.get('payment_method')

        shipping_address = {
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'email': data.get('email'),
            'phone': data.get('phone'),
            'line1': data.get('line1'),
            'region': data.get('region'),
            'province': data.get('province'),
            'city': data.get('city'),
            'barangay': data.get('barangay'),
            'postcode': data.get('postcode'),
        }

        # Save the address to session
        self.request.session['shipping_address'] = shipping_address
        print(f"Address: {shipping_address}")

        region = shipping_address['region']
        orders = self.get_orders()
        updated_orders = []
        total_shipping = Decimal(0)
        total_payment = Decimal(0)

        # Calculate shipping fees and update orders
        for shop, order_data in orders.items():
            if isinstance(order_data, dict) and 'subtotal' in order_data:
                qty = sum(item['quantity'] for item in order_data['items'])
                shipping_fee = Decimal(self.calculate_shipping_fee(region, {'shop': shop, 'qty': qty}))
                total_shipping += shipping_fee
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

        # Return a JsonResponse if the request was made via AJAX
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'updated_orders': updated_orders,
                'total_shipping': str(total_shipping),
                'total_payment': str(total_payment),
            })

        # Otherwise, redirect to the success URL or the same page with updated parameters
        return redirect(self.template_name + '?' + urlencode(self.request.GET))

    def calculate_shipping_fee(self, region, order):
        FIXED_SHIPPING_FEE = SiteSetting.get_fixed_shipping_fee()

        if FIXED_SHIPPING_FEE > 0:
            return FIXED_SHIPPING_FEE
        else:
            qty = order['qty']
            return sf_calculator(region=region, qty=qty)

    def get_orders(self):
        return self.request.session.get('ordered_items_by_shop', {})


#########################
# Set Order to Complete #
#########################

def submit_checkout(request):
    request_token_url = 'https://dashboard.twcako.com/order/api/token/refresh/'
    order_url = 'https://dashboard.twcako.com/order/api/create-order/'
    refresh_token = settings.RESPONSE_TOKEN
    token_data = {"refresh": refresh_token}
    headers = {'Content-Type': 'application/json'}

    token = requests.post(request_token_url, json=token_data, headers=headers)
    response_data = token.json()
    access_token = response_data.get('access')

    # If the request method is POST, handle the form submission
    if request.method == 'GET':
        # Get the referrer's username from the POST data

        payment_method = request.GET.get('payment_method', 'Cash On Delivery')

        ordered_items_by_shop = request.session.get('ordered_items_by_shop', {})
        address_from_session = request.session.get('shipping_address', {})

        customer_email = address_from_session.get('email')
        first_name = address_from_session.get('first_name')
        last_name = address_from_session.get('last_name')
        customer_name = f"{address_from_session.get('first_name')} {address_from_session.get('last_name')}"
        customer_phone = address_from_session.get('phone')

        shipping_amount = float(SiteSetting.get_fixed_shipping_fee())

        print(f'Email: {customer_email}')

        # Prepare ordered items list
        items = []
        shop_count = 0
        total_barley_point = 0

        for shop, shop_data in ordered_items_by_shop.items():
            shop_count += 1
            for item in shop_data['items']:
                items.append({
                    "name": item['product']['name'],
                    "quantity": item['quantity'],
                    "price": float(item['product']['price']),
                })

        # Generate unique invoice ID
        unique_invoice_id = []


        referrer_username = request.GET.get('username')

        if referrer_username:
            # API URL to check if the referrer username exists in the system
            api_url = f'https://dashboard.twcako.com/account/api/check-username/{referrer_username}/'

            try:
                if referrer_username != 'admin':
                    # Make an API request to validate the referrer username
                    response = requests.get(api_url)
                    response.raise_for_status()  # Raise an error for bad HTTP status codes
                    data = response.json()

                    # Ensure the API response is a valid JSON object
                    if not isinstance(data, dict):
                        raise ValueError("API response is not a valid JSON object")

                    # Check if the API response indicates success
                    is_success = data.get('success')
                    messenger_link = data.get('messenger_link')
                    sponsor_mobile = data.get('mobile')
                    order_complete = True
                    request.session['order_complete'] = order_complete
                    request.session['referrer'] = referrer_username
                    request.session['messenger_link'] = messenger_link
                    request.session['sponsor_mobile'] = sponsor_mobile
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

        # if customer_email:
        #     subject = 'TWC Online Store Order'
        #     message = f'Good Day {customer_name},\n\n\nYou have successfully registered an account on TWConline.store!!\n\n\nHere are your temporary account details:\n\nUsername: {first_name}\nPassword: {last_name}\n\n\nThank you for your order!'
        #     from_email = 'TWCAKO <support@twcako.com>'
        #     recipient_list = [customer_email]
        #
        #     try:
        #         send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        #         print("Email sent successfully!")
        #     except Exception as e:
        #         print(f"Error sending email: {e}")

        shipping_details = {
            "first_name": first_name,
            "last_name": last_name,
            "mobile": customer_phone,
            "address": address_from_session.get('line1'),
            "barangay": address_from_session.get('barangay'),
            "region": address_from_session.get('region'),
            "city": address_from_session.get('city'),
            "province": address_from_session.get('province'),
            "country": 'Philippines',
            "postal_code": address_from_session.get('postcode'),
            "shipping_notes": address_from_session.get('message', "")}


        for shop, shop_data in ordered_items_by_shop.items():
            cart_items = []
            shop_total_barley_point = 0

            for item in shop_data['items']:
                product_name = item['product']['name']
                barley_point = item['product'].get('barley_point', 0)
                quantity = item.get('quantity', 1)

                # Debugging to check individual values
                print(f"Product: {product_name}, Barley Point: {barley_point}, Quantity: {quantity}")

                # Multiply the barley point by the quantity and add to total
                shop_total_barley_point += barley_point * quantity
                cart_items.append({
                    'sku': item['product']['id'],
                    'qty': item['quantity'],
                })

            cod_amount = ordered_items_by_shop[shop]['cod_amount']
            discount_price = ordered_items_by_shop[shop].get('discount', 0)
            print(f'Total Barley Point: {shop_total_barley_point} for shop: {shop}')

            const_data = {
                "username": request.session['referrer'],
                "shipping_details": shipping_details,
                "order_details": {
                    "cod_amount": cod_amount,
                    "discount_price": discount_price,
                    "payment_method": "cod",
                },
                "cart_items": cart_items,
                "barley_point": shop_total_barley_point,
            }

            print(f'const_data: {const_data}')

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            response = requests.post(order_url, json=const_data, headers=headers)

            if response.status_code == 201:
                print("Order created successfully:", response.json())
                order_data = response.json()  # Get the order data from the response
                order_number = order_data.get('order_number')

                unique_invoice_id.append(order_number)
                print(f"Order number set in session: {order_number}")

                ordered_items_by_shop[shop]['order_number'] = order_number
            else:
                print("Error creating order:", response.status_code, response.text)
                return redirect('cart:cart')


        request.session['payment_method'] = payment_method
        # Handle Xendit payment method
        if payment_method == 'xendit':
            success_redirect_url = request.build_absolute_uri(reverse('cart:checkout_complete'))
            failure_redirect_url = request.build_absolute_uri(reverse('cart:cart'))
            return create_xendit_invoice(
                customer_name=customer_name,
                customer_email=customer_email,
                customer_phone=customer_phone,
                items=items,
                shipping_amount=shipping_amount,
                unique_invoice_id=unique_invoice_id,
                success_redirect_url = success_redirect_url,
                failure_redirect_url = failure_redirect_url,
                shop_count=shop_count,
            )

        return redirect('cart:checkout_complete')

    return redirect('cart:cart')


#########################
# PROMO BUNDLE CHECKOUT #
#########################


class PromoCheckoutView(View):
    template_name = 'cart/bundle-checkout.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = {}
        ordered_items_by_shop = self.request.session.get('ordered_items_by_shop', {})
        address = self.request.session.get('shipping_address')

        context.update({
            'address': address,
            'referred_by': self.request.session['referrer'],
            'order': ordered_items_by_shop,
        })
        return context


#########################################################
# ------------------checkout is done---------------------#
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
        total_quantity = 0
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
        sponsor_mobile = self.request.session.get('sponsor_mobile')
        payment_method = self.request.session.get('payment_method')
        print(f'Selected Payment Method: {payment_method}')

        region_name = address_from_session.get('region', 'Unknown')
        region_detected = detect_region(region_name)

        print(f'region_detected: {region_detected}')
        print(f'Referrer saved: {self.request.session.get("referrer")}')
        print(f'Orders: {orders}')
        print(f'Address: {address_from_session}')

        for shop, shop_data in orders.items():
            items = shop_data['items']
            total_quantity = sum(item['quantity'] for item in items)
            orders[shop]['total_quantity'] = total_quantity


        total_cod_amount = sum(Decimal(shop['cod_amount']) for shop in orders.values())
        # Update the context with data retrieved from the session
        cart_total = self.request.session['cart_total']
        context.update({
            'title': self.title,
            'sponsor_mobile': sponsor_mobile,
            'orders': orders,
            'checkout_details': checkout_details,
            'address': address_from_session,
            'total_payment': total_payment,
            'current_date': current_date,
            'sponsor': self.request.session.get('referrer', 'No referrer set'),
            'total_cod_amount': total_cod_amount,
            'detect_region': region_detected,
            'payment_method': payment_method,
        })

        return context


def set_order_id_session_variable(request):
    if request.method == 'POST' and request.is_ajax():
        order_id = request.POST.get('order_id')
        request.session['clicked_order_id'] = order_id
        print(f'Order ID: {order_id}')
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


#########################################################
# ----------Change address from list of addresses--------#
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
# -------Edit an address from the list of addresses------#
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