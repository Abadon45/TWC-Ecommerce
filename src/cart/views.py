import json

from django.utils import timezone
from django.core import signing
from django.core.signing import BadSignature
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from urllib.parse import urlencode

from onlinestore.api import *
from onlinestore.catalog import get_product_by_slug
from onlinestore.forms import AddressForm
from .utils import *

DEMO_ORDER_COOKIE = 'twcDemoOrder'
DEMO_ADDRESS_COOKIE = 'twcDemoAddress'


def fetch_product_quantity(request):
    product_slug = request.GET.get('slug')

    if not product_slug:
        return JsonResponse({'error': 'Product slug is required.'}, status=400)

    try:
        quantity, supplier_product = fetch_quantity_api(product_slug)
        return JsonResponse({'slug': product_slug, 'quantity': quantity, 'supplier_product': supplier_product})

    except Http404 as e:
        return JsonResponse({'error': str(e)}, status=404)

    except Exception as e:
        print(f"Unexpected error: {e}")
        return JsonResponse({'error': 'An unexpected error occurred.'}, status=500)



class UpdateCartView(View):
    def get_product_data(self, product_slug):
        """Read product data from the local catalog snapshot."""
        return get_product_by_slug(product_slug)

    def update_cart(self, request, product_slug, action, quantity):
        """Update the cart stored in the session."""
        # Fetch product data from the API
        product = self.get_product_data(product_slug)
        MAX_ORDER_QUANTITY = int(SiteSetting.get_max_order_quantity())
        if MAX_ORDER_QUANTITY <= 0:
            MAX_ORDER_QUANTITY = 999

        max_order_exceeded = False
        message = "Cart updated"

        order_complete = False
        self.request.session['order_complete'] = order_complete

        print(f'max_order_quantity: {MAX_ORDER_QUANTITY}')

        if not product:
            return None, 'Product not found or API error'

        # Retrieve the cart from the session, or create an empty one
        cart = get_cart_cookie(request) or request.session.get('cart', {})

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
                    'total_quantity': 0,
                    'subtotal': 0,
                    'shipping_fee': 0,
                    'discount': 0,
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

        self.request.session['cart_total'] = 0
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
            self.request.session['cart_total'] += cod_amount

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
        response = JsonResponse({
            'error': False,
            'message': message,
            'cart_items': total_items,
            'total_cart_price': total_price,
            'cart': cart,
            'shop_cart': ordered_items_by_shop,
            'max_order_exceeded': max_order_exceeded,
        }, status=200)
        return set_cart_cookie(response, cart)


class CheckoutView(View):
    template_name = 'cart/shop-checkout.html'

    def get_context_data(self, **kwargs):
        print(f'Orders: {self.get_orders()}')
        num_shops = len(self.get_orders().keys())
        multishop = False
        if num_shops > 1:
            multishop = True
        context = {
            'multishop': multishop,
            'shipping_form': AddressForm(),
            'orders': self.get_orders(),
            'cart_total': self.request.session.get('cart_total', 0),
            'referred_by': self.request.session.get('referrer'),
            'title': "Checkout",
            # The signed snapshot is a fallback for browsers where the legacy
            # duplicate address requests rotate or lose the session state.
            'checkout_snapshot': signing.dumps(self.get_orders()),
        }
        return context

    def get(self, request, *args, **kwargs):
        orders = self.get_orders()
        if not orders:
            return redirect('shop:shop')

        if 'full_name' in request.GET:  # Check if the form was submitted
            return self.process_shipping_info(request.GET)

        context = self.get_context_data()
        response = render(request, self.template_name, context)
        response.set_cookie(
            DEMO_ORDER_COOKIE,
            signing.dumps(context['orders']),
            max_age=60 * 60 * 24,
            secure=not settings.DEBUG,
            httponly=False,
            samesite='Lax',
        )
        return response

    def process_shipping_info(self, data):

        shipping_address = {
            'full_name': data.get('full_name'),
            'phone': data.get('phone'),
            'address': data.get('address'),
            'province': data.get('province'),
            'city': data.get('city'),
            'barangay': data.get('barangay'),
            'landmark': data.get('landmark'),
        }

        # Save the address to session
        if 'shipping_address' in self.request.session:
            del self.request.session['shipping_address']
        self.request.session['shipping_address'] = shipping_address

        print(f"Address: {shipping_address}")

        region = shipping_address['province']
        orders = self.get_orders()
        updated_orders = []
        total_shipping = Decimal(0)
        total_payment = Decimal(0)
        shop_count = 0

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
        self.request.session['checkout_order_snapshot'] = orders
        # Dedicated demo-only snapshot consumed by the thank-you page.
        self.request.session['thank_you_order'] = orders
        self.request.session['checkout_completed'] = False
        self.request.session.modified = True

        # Return a JsonResponse if the request was made via AJAX
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            response = JsonResponse({
                'status': 'success',
                'updated_orders': updated_orders,
                'total_shipping': str(total_shipping),
                'total_payment': str(total_payment),
            })
            response.set_cookie(
                DEMO_ADDRESS_COOKIE,
                signing.dumps(shipping_address),
                max_age=60 * 60 * 24,
                secure=not settings.DEBUG,
                httponly=False,
                samesite='Lax',
            )
            return response

        # Otherwise, redirect to the success URL or the same page with updated parameters
        response = redirect(reverse('cart:checkout') + '?' + urlencode(self.request.GET))
        response.set_cookie(
            DEMO_ADDRESS_COOKIE,
            signing.dumps(shipping_address),
            max_age=60 * 60 * 24,
            secure=not settings.DEBUG,
            httponly=False,
            samesite='Lax',
        )
        return response

    def calculate_shipping_fee(self, region, order):
        FIXED_SHIPPING_FEE = SiteSetting.get_fixed_shipping_fee()

        if FIXED_SHIPPING_FEE > 0:
            return FIXED_SHIPPING_FEE
        else:
            qty = order['qty']
            return sf_calculator(province=region, qty=qty)

    def get_orders(self):
        orders = self.request.session.get('ordered_items_by_shop', {})
        if orders:
            return orders

        # The drawer can start checkout directly from the shop. Hydrate the
        # legacy checkout session from the same browser cart cookie instead of
        # redirecting back to the shop because the old session is empty.
        cart = get_cart_cookie(self.request)
        if not cart:
            return {}

        cart_builder = UpdateCartView()
        cart_builder.request = self.request
        orders = cart_builder._rebuild_ordered_items_by_shop(cart)
        self.request.session['cart'] = cart
        self.request.session['ordered_items_by_shop'] = orders
        self.request.session.modified = True
        return orders


#########################
# Set Order to Complete #
#########################


def complete_checkout_locally(request):
    """Finish the legacy checkout without calling the retired order API.

    The original storefront delegated final order creation to the dashboard
    service. That service is no longer part of this legacy app, so the local
    checkout snapshot is now the completed-order record used by the thank-you
    page.
    """
    # The legacy dashboard/order API is retired.  The checkout confirmation
    # must therefore be built from a local, immutable session snapshot.
    orders = (
        request.session.get('thank_you_order')
        or
        request.session.get('checkout_order_snapshot')
        or request.session.get('ordered_items_by_shop')
        or request.session.get('demo_order_snapshot')
        or request.session.get('orders')
    )
    if not orders:
        snapshot_token = request.GET.get('checkout_snapshot')
        if snapshot_token:
            try:
                orders = signing.loads(snapshot_token)
            except (BadSignature, ValueError, TypeError):
                orders = {}
    if not orders:
        snapshot_token = request.COOKIES.get(DEMO_ORDER_COOKIE)
        if snapshot_token:
            try:
                orders = signing.loads(snapshot_token)
            except (BadSignature, ValueError, TypeError):
                orders = {}
    # The drawer is cookie-backed. Rehydrate the legacy session at the final
    # step as well, because a checkout can be opened in a fresh session or
    # after the session snapshot has expired.
    if not orders:
        cart = get_cart_cookie(request) or request.session.get('cart', {})
        if cart:
            cart_builder = UpdateCartView()
            cart_builder.request = request
            orders = cart_builder._rebuild_ordered_items_by_shop(cart)
            request.session['cart'] = cart
            request.session['ordered_items_by_shop'] = orders
            request.session.modified = True
    if not orders:
        return JsonResponse({
            'error': 'Your checkout has no items. Please return to the shop.'
        }, status=400)

    # Payment providers are intentionally bypassed for this demo.  Keep the
    # selected value out of the result so a stale xendit value can never send
    # the customer back into the retired integration.
    payment_method = 'cod'

    order_number = request.session.get('invoice_number') or generate_invoice_number()
    for shop_data in orders.values():
        shop_data['order_number'] = order_number

    request.session['ordered_items_by_shop'] = orders
    request.session['orders'] = orders
    request.session['demo_order_snapshot'] = orders
    request.session['thank_you_order'] = orders
    request.session['demo_order_status'] = 'completed'
    request.session['payment_method'] = payment_method
    request.session['invoice_number'] = order_number
    request.session['order_complete'] = True
    request.session['checkout_completed'] = True

    username = request.GET.get('username')
    if username:
        request.session['referrer'] = username
    request.session.modified = True

    thank_you_url = reverse('cart:checkout_complete')
    if request.headers.get('x-requested-with') != 'XMLHttpRequest':
        # Progressive-enhancement fallback: if checkout JavaScript is blocked
        # or fails to load, a regular form submit still completes the demo
        # order and reaches the confirmation page.
        response = redirect(thank_you_url)
    else:
        response = JsonResponse({
            'redirect_url': request.build_absolute_uri(thank_you_url),
            'payment_method': payment_method,
            'local_completion': True,
            'demo_order': True,
        })
    response.set_cookie(
        DEMO_ORDER_COOKIE,
        signing.dumps(orders),
        max_age=60 * 60 * 24,
        secure=not settings.DEBUG,
        httponly=False,
        samesite='Lax',
    )
    address = request.session.get('shipping_address')
    if address:
        response.set_cookie(
            DEMO_ADDRESS_COOKIE,
            signing.dumps(address),
            max_age=60 * 60 * 24,
            secure=not settings.DEBUG,
            httponly=False,
            samesite='Lax',
        )
    # A completed order must not reappear in the next shopping session.
    response.delete_cookie(USER_CART_COOKIE, path='/')
    return response


def submit_checkout(request):
    return complete_checkout_locally(request)


def submit_promo_checkout(request):
    return complete_checkout_locally(request)


#########################
# PROMO BUNDLE CHECKOUT #
#########################


class PromoCheckoutView(CheckoutView):
    title = "Promo Checkout"
    template_name = 'cart/bundle-checkout.html'

    def get_context_data(self, **kwargs):
        # Get the default context from the parent class
        context = super().get_context_data(**kwargs)

        # Ensure 'unique_id' exists in the session or generate a new one
        unique_id = self.request.session.get('unique_id', generate_invoice_number())
        if 'unique_id' not in self.request.session:
            self.request.session['unique_id'] = unique_id

        event_id = f'checkout_{unique_id}'

        selling_capi_token = self.request.session.get('selling_capi_token', None)
        sponsor_fb_pixel = self.request.session.get('sponsor_fb_pixel', None)
        event_name = self.request.session.get('event_name', None)

        if selling_capi_token and sponsor_fb_pixel:
            # FUNNEL INTEGRATIONS
            external_id = unique_id
            fbp = self.request.COOKIES.get('_fbp')
            fbc = self.request.COOKIES.get('_fbc')

            try:
                client_ip_address = get_client_ip(self.request)
                client_user_agent = get_client_user_agent(self.request)
                capi_token = selling_capi_token
                first_name = self.request.GET.get('fn', '')
                last_name = self.request.GET.get('ln', '')
                mobile = self.request.GET.get('mobile', '')

                user_data = UserData(
                    first_name=first_name,
                    last_name=last_name,
                    phone=mobile if mobile else "",
                    external_id=external_id,
                    client_ip_address=client_ip_address,
                    client_user_agent=client_user_agent,
                    fbp=fbp,
                    fbc=fbc
                )

                custom_data = CustomData(
                    content_name=event_name,
                )

                conversion_api(
                    self.request,
                    access_token=capi_token,
                    pixel_id=sponsor_fb_pixel,
                    event_name=event_name,
                    event_id=event_id,
                    user_data=user_data,
                    custom_data=custom_data
                )
            except Exception as e:
                # Log the exception for debugging purposes
                print(f"Conversion API error: {e}")

        context['event_id'] = event_id
        context['title'] = self.title
        context['event_name'] = self.request.session.get('event_name', "")

        return context


#########################################################
# ------------------checkout is done---------------------#
#########################################################


class CheckoutDoneView(View):
    title = "Thank You"
    template_name = 'cart/shop-checkout-complete.html'

    def get(self, request, *args, **kwargs):
        # Check if 'order_complete' exists in the session
        order_complete = request.session.get('order_complete', False)
        has_demo_snapshot = bool(request.session.get('demo_order_snapshot'))
        has_thank_you_order = bool(request.session.get('thank_you_order'))
        request.session['promo'] = False

        # Recover the dedicated demo order from the cart cookie if the
        # duplicate legacy checkout requests rotated the session.
        if not order_complete and not has_demo_snapshot and not has_thank_you_order:
            cart = get_cart_cookie(request)
            if cart:
                cart_builder = UpdateCartView()
                cart_builder.request = request
                thank_you_order = cart_builder._rebuild_ordered_items_by_shop(cart)
                request.session['thank_you_order'] = thank_you_order
                request.session['demo_order_snapshot'] = thank_you_order
                request.session['order_complete'] = True
                request.session['demo_order_status'] = 'completed'
                request.session.modified = True
                has_thank_you_order = True

        if not order_complete and not has_demo_snapshot and not has_thank_you_order:
            snapshot_token = request.COOKIES.get(DEMO_ORDER_COOKIE)
            if snapshot_token:
                try:
                    thank_you_order = signing.loads(snapshot_token)
                except (BadSignature, ValueError, TypeError):
                    thank_you_order = {}
                if thank_you_order:
                    request.session['thank_you_order'] = thank_you_order
                    request.session['demo_order_snapshot'] = thank_you_order
                    request.session['order_complete'] = True
                    request.session['demo_order_status'] = 'completed'
                    request.session.modified = True
                    has_thank_you_order = True

        # Redirect to home if the order is not complete
        if not order_complete and not has_demo_snapshot and not has_thank_you_order:
            return redirect("shop:shop")

        # Prepare the context data for rendering
        context = self.get_context_data()

        # Render the template with the context
        return render(request, self.template_name, context)

    def get_context_data(self):
        context = {}

        total_payment = 0.0
        total_quantity = 0
        current_date = timezone.now().strftime('%b %d, %Y')

        # Retrieve ordered_items_by_shop and total_cart_subtotal from the session
        request = self.request
        request.session['checkout_completed'] = False
        if request.session.get('thank_you_order'):
            orders = request.session.get('thank_you_order', {})
            request.session['orders'] = orders
        elif request.session.get('ordered_items_by_shop'):
            ordered_items_by_shop = request.session.get('ordered_items_by_shop', {})
            orders = ordered_items_by_shop.copy()

            request.session.pop('cart', None)
            request.session.pop('ordered_items_by_shop', None)

            request.session['orders'] = orders
        else:
            orders = request.session.get('demo_order_snapshot') or request.session.get('orders', {})

        checkout_details = request.session.get('updated_orders', {})
        address_from_session = request.session.get('shipping_address', {})
        if not address_from_session:
            address_token = request.COOKIES.get(DEMO_ADDRESS_COOKIE)
            if address_token:
                try:
                    address_from_session = signing.loads(address_token)
                except (BadSignature, ValueError, TypeError):
                    address_from_session = {}
        sponsor_mobile = request.session.get('sponsor_mobile')
        payment_method = request.session.get('payment_method')
        print(f'Selected Payment Method: {payment_method}')

        province_name = address_from_session.get('province', 'Unknown')
        region_detected = detect_region(province_name)

        print(f'region_detected: {region_detected}')
        print(f'Referrer saved: {request.session.get("referrer")}')
        print(f'Orders: {orders}')
        print(f'Address: {address_from_session}')

        for shop, shop_data in orders.items():
            items = shop_data['items']
            total_quantity = sum(item['quantity'] for item in items)
            orders[shop]['total_quantity'] = total_quantity

        total_cod_amount = sum(Decimal(shop['cod_amount']) for shop in orders.values())
        # Update the context with data retrieved from the session
        cart_total = request.session.get('cart_total', 0)  # Add a default value if needed
        context.update({
            'title': self.title,
            'sponsor_mobile': sponsor_mobile,
            'orders': orders,
            'checkout_details': checkout_details,
            'address': address_from_session,
            'total_payment': total_payment,
            'current_date': current_date,
            'sponsor': request.session.get('referrer', 'No referrer set'),
            'total_cod_amount': total_cod_amount,
            'detect_region': region_detected,
            'payment_method': payment_method,
            'invoice_number': request.session.get('invoice_number', ""),
            'cart_total': cart_total,
            'demo_order': request.session.get('demo_order_status') == 'completed',
        })

        return context


class PromoCheckoutDoneView(CheckoutDoneView):
    title = "Thank You"
    template_name = 'cart/bundle-thank-you.html'

    def get_context_data(self, **kwargs):
        # Get the default context from the parent class
        context = super().get_context_data(**kwargs)

        unique_id = self.request.session.get('unique_id', generate_invoice_number())
        if 'unique_id' not in self.request.session:
            self.request.session['unique_id'] = unique_id

        event_id = f'thank-you-page_{unique_id}'

        selling_capi_token = self.request.session.get('selling_capi_token', None)
        sponsor_fb_pixel = self.request.session.get('sponsor_fb_pixel', None)
        event_name = self.request.session.get('event_name', None)

        if selling_capi_token and sponsor_fb_pixel:
            # FUNNEL INTEGRATIONS
            external_id = unique_id
            fbp = self.request.COOKIES.get('_fbp')
            fbc = self.request.COOKIES.get('_fbc')

            try:
                client_ip_address = get_client_ip(self.request)
                client_user_agent = get_client_user_agent(self.request)
                capi_token = selling_capi_token
                first_name = self.request.GET.get('fn', '')
                last_name = self.request.GET.get('ln', '')
                mobile = self.request.GET.get('mobile', '')

                user_data = UserData(
                    first_name=first_name,
                    last_name=last_name,
                    phone=mobile if mobile else "",
                    external_id=external_id,
                    client_ip_address=client_ip_address,
                    client_user_agent=client_user_agent,
                    fbp=fbp,
                    fbc=fbc
                )

                custom_data = CustomData(
                    content_name=event_name,
                )

                conversion_api(
                    self.request,
                    access_token=capi_token,
                    pixel_id=sponsor_fb_pixel,
                    event_name=event_name,
                    event_id=event_id,
                    user_data=user_data,
                    custom_data=custom_data
                )
            except Exception as e:
                print(f"Error in conversion API: {e}")

        context['event_id'] = event_id
        context['title'] = self.title
        context['event_name'] = self.request.session.get('event_name', "")

        return context
