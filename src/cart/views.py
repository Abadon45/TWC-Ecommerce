import json

from django.utils import timezone
from django.shortcuts import redirect, render
from django.utils.html import format_html
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from urllib.parse import urlencode
from cart.utils import send_email
from decimal import Decimal

from onlinestore.api import *
from onlinestore.forms import AddressForm
from .utils import *



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
            cart_total += int(cod_amount)

        self.request.session['cart_total'] = cart_total
        # Update the context with data retrieved from the session
        context.update({
            'title': self.title,
            'ordered_items_by_shop': ordered_items_by_shop,
            'cart_total': cart_total,
        })

        return context


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
        """Fetch product data from the API."""
        product_url = f'{settings.PRODUCT_URL_API}{product_slug}'
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
        print(f'Orders: {self.get_orders()}')
        num_shops = len(self.get_orders().keys())
        multishop = False
        referrer = get_referrer_from_host(self.request)

        if num_shops > 1:
            multishop = True

        context = {
            'multishop': multishop,
            'shipping_form': AddressForm(),
            'orders': self.get_orders(),
            'cart_total': self.request.session.get('cart_total', 0),
            'referred_by': referrer,
            'title': "Checkout",
        }
        return context

    def get(self, request, *args, **kwargs):
        orders = self.get_orders()
        if not orders:
            return redirect('shop:shop')

        if 'full_name' in request.GET:  # Check if the form was submitted
            return self.process_shipping_info(request.GET)

        context = self.get_context_data()
        return render(request, self.template_name, context)

    def process_shipping_info(self, data):

        shipping_address = {
            'full_name': data.get('full_name'),
            'phone': data.get('phone'),
            'email': data.get('email'),
            'address': data.get('address'),
            'province': data.get('province'),
            'city': data.get('city'),
            'barangay': data.get('barangay'),
            'landmark': data.get('landmark'),
        }

        self.request.session['temp_username'] = data.get('username')
        self.request.session['temp_password'] = generate_random_password()
        self.request.session['email'] = data.get('email')

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
        self.request.session['checkout_completed'] = False

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
    ordered_items_by_shop = request.session.get('ordered_items_by_shop', {})
    cart = request.session.get('cart', {})  # Retrieve the cart from the session
    temp_username = request.session.get('temp_username')
    temp_password = request.session.get('temp_password')
    email = request.session.get('email')
    sponsor = get_referrer_from_host(request)
    user = request.user
    access_token = get_access_token()

    if sponsor == None:
        sponsor = temp_username

    print(f'temp_username: {temp_username}, temp_password: {temp_password}')

    if not user.is_authenticated:
        if temp_password and temp_username:
            REGISTER_USER_API_URL = settings.REGISTER_USER_API_URL
            # Retrieve email from shipping_address stored in the session
            shipping_address = request.session.get('shipping_address', {})
            email = shipping_address.get('email')

            if not email or email == 'undefined':
                email = None

            register_data = {
                "username": temp_username,
                "email": email,
                "password": temp_password,
                "is_customer": True,
                "sponsor_username": sponsor,
            }

            headers = {
                "Content-Type": "application/json"
            }
            if access_token:
                headers["Authorization"] = f"Bearer {access_token}"  # Add token if available

            print(f"Registering user: {register_data}")

            try:
                response = requests.post(REGISTER_USER_API_URL, json=register_data, headers=headers)

                print(f"Response Status: {response.status_code}")
                print(f"Response Content (Raw): {response.text}")  # Print raw response

                api_response = response.json()  # This is where the error occurs

                print(f"Response Content (Parsed JSON): {api_response}")

                if response.status_code != 201:
                    return JsonResponse({
                        'error': f'User registration failed. {api_response.get("message", "Please try again.")}',
                        'status_code': response.status_code
                    }, status=400)

                print(f"User {temp_username} registered successfully!")

            except requests.RequestException as e:
                print(f"Error: {e}")
                return JsonResponse({'error': 'Failed to register user. Please try again later.'}, status=500)

            except json.JSONDecodeError:
                print("Error: Response is not valid JSON.")
                return JsonResponse({'error': 'Invalid response from the server. Please try again later.'}, status=500)

    for shop, shop_data in ordered_items_by_shop.items():

        for item in shop_data['items']:
            product_name = item['product']['name']
            product_quantity = item.get('quantity', 1)
            slug = item['product']['slug']

            quantity, supplier_product = fetch_quantity_api(slug)
            quantity = int(quantity)

            if int(product_quantity) > quantity and supplier_product:
                message = f'{product_name} stock exceeds quantity of available stock: {quantity}'
                item['quantity'] = quantity

                if slug in cart:
                    cart[slug]['quantity'] = quantity

                if int(quantity) == 0:
                    message = f'{product_name} is out of stock, deleting your product from the cart'
                    shop_data['items'].remove(item)
                    if slug in cart:
                        del cart[slug]

                request.session['ordered_items_by_shop'] = ordered_items_by_shop
                request.session['cart'] = cart
                return JsonResponse({
                    'error': message,
                    'redirect_url': reverse('cart:cart'),
                }, status=400)


    if not access_token:
        return JsonResponse({
            'error': 'Failed to retrieve access token. Please try again later.'
        }, status=400)
    return submit_checkout_base(request)


def submit_promo_checkout(request):
    access_token = get_access_token()
    if not access_token:
        return JsonResponse({
            'error': 'Failed to retrieve access token. Please try again later.'
        }, status=400)
    return submit_checkout_base(request)


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

        context['sponsor'] = self.request.session.get('sponsor_username', None)
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
        order_complete = request.session.get('order_complete', False)
        request.session['promo'] = False

        if not order_complete:
            return redirect("home_view")

        context = self.get_context_data()

        # Send confirmation email
        self.send_confirmation_email(context)

        return render(request, self.template_name, context)

    def get_context_data(self):
        context = {}
        total_payment = 0.0
        current_date = timezone.now().strftime('%b %d, %Y')

        request = self.request
        request.session['checkout_completed'] = False

        # Preserve orders session to prevent loss on refresh
        if 'ordered_items_by_shop' in request.session:
            ordered_items_by_shop = request.session.pop('ordered_items_by_shop', {})
            orders = ordered_items_by_shop.copy()
            request.session.pop('cart', None)
            request.session['orders'] = orders  # Store the orders in session
        else:
            orders = request.session.get('orders', {})

        checkout_details = request.session.get('updated_orders', {})
        address_from_session = request.session.get('shipping_address', {})
        sponsor_mobile = request.session.get('mobile')
        payment_method = request.session.get('payment_method')

        province_name = address_from_session.get('province', 'Unknown')
        region_detected = detect_region(province_name)

        for shop, shop_data in orders.items():
            items = shop_data.get('items', [])
            total_quantity = sum(item.get('quantity', 0) for item in items)
            orders[shop]['total_quantity'] = total_quantity

        try:
            total_cod_amount = sum(Decimal(shop.get('cod_amount', 0)) for shop in orders.values())
        except Exception as e:
            print(f"❌ Error calculating COD amount: {e}")
            total_cod_amount = 0

        cart_total = request.session.get('cart_total', 0)

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
            'username': request.session.get('temp_username', ""),
            'password': request.session.get('temp_password', ""),
            'email': request.session.get('email', ""),
        })

        return context

    def send_confirmation_email(self, context):
        """Send a confirmation email with temporary login details."""
        user_email = context.get("email")
        username = context.get("username")
        password = context.get("password")
        orders = context.get("orders", {})

        if user_email and username and password:
            subject = "Welcome to TWCAKO - Your Account & Order Details"

            # Generate order details safely
            order_details_list = []
            for shop, shop_data in orders.items():
                items_list = ", ".join(
                    f"{item['product'].get('name', 'Unknown Item')} (x{item.get('quantity', 0)})"
                    for item in shop_data.get('items', [])
                )
                order_details_list.append(f"<li><strong>{shop}:</strong> {items_list}</li>")

            order_details_html = "".join(order_details_list)

            html_content = f"""
                <p>Dear Customer,</p>
                <p>Thank you for shopping with TWCAKO. Below are your temporary login details:</p>
                <ul>
                    <li><strong>Username:</strong> {username}</li>
                    <li><strong>Password:</strong> {password}</li>
                </ul>
                <p>Please change your password after logging in for security purposes.</p>

                <h3>Your Order Details:</h3>
                <ul>
                    {order_details_html}
                </ul>

                <p>If you have any questions, feel free to contact our support team.</p>
                <p>Best regards,</p>
                <p><strong>TWCAKO Support Team</strong></p>
            """

            try:
                send_email(user_email, subject, html_content, from_email="support@twcako.com")
                print(f"✅ Email sent successfully to {user_email}")
            except Exception as e:
                print(f"❌ Failed to send email: {e}")


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

