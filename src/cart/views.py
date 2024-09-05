from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.views import View
from django.views.generic import TemplateView
from django.db import transaction
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

from .models import *
from .forms import AddressForm
from onlinestore.models import SiteSetting
from onlinestore.utils import send_temporary_account_email
from .utils import sf_calculator

import json
import requests


User = get_user_model()


class CartView(TemplateView):
    template_name = 'cart/shop-cart.html'
    title = "Cart"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Filters Existing Orders from different shops
        order_ids = self.request.session.get('checkout_orders', [])
        orders = Order.objects.filter(id__in=order_ids) 
            
        ordered_items = {}
        for order in orders:
            ordered_items[order] = OrderItem.objects.filter(order=order).select_related('product')
            
        total_cart_subtotal = sum(order.calculate_subtotal() for order in orders)
        
        context.update({
            'title': self.title,
            'orders': orders,
            'ordered_items': ordered_items,
            'total_cart_subtotal': total_cart_subtotal,
        })
        
        return context


@transaction.atomic
def updateItem(request):
    MAX_ORDER_QUANTITY = int(SiteSetting.get_max_order_quantity())
    bundleDetails = json.loads(request.GET.get('bundleDetails', '{}'))
    productId = request.GET.get('productId')
    action = request.GET.get('action')
    quantity = int(request.GET.get('quantity', 1))

    max_order_exceeded = False
    supplier = None

    user = request.user
    session_key = request.session.session_key

    print(f'Products for sales funnel: {bundleDetails}')

    # Remove session data related to completed checkout
    if 'checkout_done_bundle' in request.session:
        del request.session['checkout_done_bundle']
    if 'checkout_done_view' in request.session:
        del request.session['checkout_done_view']

    # Initialize or retrieve the session key if not already present
    if not session_key:
        request.session.save()
        session_key = request.session.session_key

    print('Action: ', action)
    print('Product: ', productId)
    print('Quantity: ', quantity)

    try:
        orderItem = None

        # Handle bundle order updates by iterating through the products in the bundle
        if bundleDetails:
            order_id = request.session['bundle_order']
            order = Order.objects.get(order_id=order_id)

            print(f'Order in UpdateItem: {order}')

            for productDetail in bundleDetails.get('products', []):
                productId = productDetail['id']
                quantity = productDetail.get('quantity', 1)

                product = get_object_or_404(Product, id=productId)
                print(productId)
                print('Product: ', productId)

                # Retrieve or create an OrderItem for each product in the bundle
                orderItem, order_item_created = OrderItem.objects.get_or_create(order=order, product=product)
                orderItem.quantity = quantity
                orderItem.save()

        else:
            product = get_object_or_404(Product, id=productId)
            supplier = product.category_1

            # Get or create the order based on user authentication and supplier
            if user.is_authenticated:
                print(f"User is authenticated: {user.username}")
                order, created = Order.objects.get_or_create(user=user, supplier=supplier, complete=False)
            else:
                print(f"User is not authenticated")
                order, created = Order.objects.get_or_create(user=None, session_key=session_key, supplier=supplier, complete=False)
            print (f'Order Quantity: {order.total_quantity}')

            # Check for maximum order quantity only for the "add" action
            if action == 'add' and 0 < MAX_ORDER_QUANTITY < order.total_quantity + quantity:
                max_order_exceeded = True
                return JsonResponse({
                    'action': action,
                    'max_order_quantity': MAX_ORDER_QUANTITY,
                    'max_order_exceeded': max_order_exceeded,
                    'message': f'Order quantity limit exceeded. Max allowed is {MAX_ORDER_QUANTITY}.',
                    'orders': [{
                        'order_id': order.order_id,
                        'subtotal': order.subtotal,
                        'order_count': order.orderitem_set.count(),
                    }],
                }, safe=False)

            # Get or create the order item only if the quantity limit is not exceeded
            orderItem, order_item_created = OrderItem.objects.get_or_create(order=order, product=product)

            # add or subtract item quantity and or remove items from the cart
            if orderItem:
                print(f"Order Item Quantity Before: {orderItem.quantity}")
                print(f"Action: {action}")

                if action == 'add':
                    orderItem.quantity += quantity
                elif action == 'minus':
                    orderItem.quantity -= quantity

                if action == 'remove' or orderItem.quantity <= 0:
                    orderItem.delete()
                    if order.orderitem_set.all().count() == 0:
                        order.delete()
                else:
                    orderItem.save()

        # Filter existing orders for the user/anonymous user
        existing_orders = Order.objects.filter(user=user, supplier=supplier, complete=False) if user.is_authenticated else \
                        Order.objects.filter(session_key=session_key, supplier=supplier, complete=False)

        # Associate order item to the order
        ordered_items = {}
        for order in existing_orders:
            ordered_items[order] = OrderItem.objects.filter(order=order).select_related('product')

        # filters incomplete orders
        if user.is_authenticated:
            orders = Order.objects.filter(user=user, complete=False)
        else:
            orders = Order.objects.filter(session_key=session_key, complete=False)

        # saves the orders to session for later use
        request.session['checkout_orders'] = list(orders.values_list('id', flat=True))

        cart_items = sum(order.total_quantity for order in orders)
        total_cart_subtotal = sum(order.calculate_subtotal() for order in orders)

        print(f'total items in cart: {cart_items}')

        return JsonResponse({
            'action': action,
            'cart_items': cart_items,
            'total_cart_subtotal': total_cart_subtotal,
            'max_order_quantity': MAX_ORDER_QUANTITY,
            'max_order_exceeded': max_order_exceeded,
            'products': [{
                'id': product.id,
                'name': product.name,
                'image': getattr(product.image_1, 'url', None) if product.image_1 else None,
                'quantity': orderItem.quantity if orderItem else 0,
                'total': orderItem.get_total if orderItem else 0,
            }],
            'orders': [{
                'order_id': o.order_id,
                'subtotal': o.subtotal,
                'order_count': o.orderitem_set.count(),
            } for o in existing_orders],
        }, safe=False)

    except Exception as e:
        print(f"Exception in updateItem: {e}")
        return JsonResponse({'error': 'Internal Server Error'}, status=500)


#----------------- Checkout Views -------------------

def checkout(request):
    title = "Checkout"
    shipping_form = AddressForm()
    order = Order()
    default_address = ""
    ordered_items = []
    customer_addresses = ""
    FIXED_SHIPPING_FEE = SiteSetting.get_fixed_shipping_fee()
    shipping_fee = 0.00
    orders_subtotal = Decimal('0.00')
    total_shipping = Decimal('0.00')
    total_discount = Decimal('0.00')
    
    user = request.user
    session_key = request.session.session_key
    referrer = None
    
    try:
        # check if user is authenticated or not and saves their sponsor to a variable if there is one
        if user.is_authenticated:
            default_address = Address.objects.filter(user=user, is_default=True).first()
            customer_addresses = Address.objects.filter(user=user).exclude(is_default=True).order_by('-is_default')[:3]
            referred_by = user.sponsor
        else:
            referred_by = request.session.get('referrer')
            
        print(f'Sponsor: {referred_by}')
        order_ids = request.session.get('checkout_orders', [])
        orders = Order.objects.filter(id__in=order_ids)

        # checks if address is there is already a default address
        if default_address:
            region = default_address.region
            print(f"Shipping Fee: {shipping_fee}")
            print(f"Address Region: {region}")
            for order in orders:
                order.shipping_address = default_address
                qty = order.total_quantity
                if order.is_fixed_shipping_fee:
                    fixed_shipping_fee = FIXED_SHIPPING_FEE
                    order.shipping_fee = fixed_shipping_fee
                else:
                    shipping_fee = sf_calculator(region=region, qty=qty)
                    order.shipping_fee = shipping_fee
                order.save()
                
        # store the order and the orderitems in the list
        for order in orders:        
            with transaction.atomic():
                existing_order_items = order.orderitem_set.all()
                print("Order items:", order.orderitem_set.all())
                for order_item in existing_order_items:
                    product = order_item.product
                    ordered_items.append(OrderItem(order=order, product=product, quantity=order_item.quantity))   
                order.save()

        # Address Form and fetching the name for account registration
        if request.method == 'POST':  
            shipping_form = AddressForm(request.POST)
            
            if shipping_form.is_valid():
                shipping_address = shipping_form.save(commit=False)
                
                region = shipping_form.cleaned_data.get('region')
                updated_orders = []

                # calculate shipping based on the fixed shipping otherwise calculate based on region
                for order in orders:
                    qty = order.total_quantity
                    if order.is_fixed_shipping_fee:
                        fixed_shipping_fee = FIXED_SHIPPING_FEE
                        order.shipping_fee = fixed_shipping_fee
                    else:
                        shipping_fee = sf_calculator(region=region, qty=qty)
                        order.shipping_fee = shipping_fee
                    order.total_amount = order.subtotal + Decimal(order.shipping_fee)
                    order.save()
                    
                    updated_orders.append({
                        'id': order.id, 
                        'shipping_fee': order.shipping_fee,
                        'total_amount': order.total_amount
                    })
                
                if user.is_authenticated:
                    shipping_address.user = user
                else:
                    shipping_address.session_key = session_key
                
                if user.is_authenticated:
                    if not Address.objects.filter(user=user, is_default=True).exists():
                        shipping_address.is_default = True

                else:
                    shipping_address.is_default = True
                    
                shipping_address.save()
                print("Shipping address created:", shipping_address)

                # register the address to the order
                if not order.shipping_address:
                    
                    for order in orders:
                        order.shipping_address = shipping_address
                        order.contact_number = shipping_address.phone
                        order.save()
                
                        print("Order Information After Address Update:", order.order_id, order.shipping_address)
                    
                    # Generate a temporary account for the Guest User
                    if request.user.is_anonymous:
                        temporary_username = request.POST.get('username').lower()  
                        print(f'username retrieved from ajax: {temporary_username}') 

                        if temporary_username:
                            print("Creating temporary user...")
                            temporary_user, user_created = User.objects.get_or_create(username=temporary_username)
                            if user_created:
                                print(f"User created: {user_created}")
                                temporary_password = User.objects.make_random_password(length=6)
                                
                                if referrer:
                                    try:
                                        temporary_user.referred_by = referrer
                                        temporary_user.save()
                                    except User.DoesNotExist:
                                        print("Referrer not found.")
                                
                                # PUT THIS ON THE FINAL VERSION
                                # if User.objects.filter(email=user.email).exists():
                                #     print("A user with this email already exists.") 
                                # else:
                                
                                
                                #---------------------------------------
                                # Transfer Details to the temporary_user
                                #---------------------------------------
                                temporary_user.email = request.POST.get('email')
                                temporary_user.set_password(temporary_password)
                                temporary_user.first_name = shipping_address.first_name
                                temporary_user.last_name = shipping_address.last_name
                                temporary_user.save()
                                shipping_address.user = temporary_user
                                shipping_address.save()
                                for order in orders:
                                    order.user = temporary_user
                                    order.save()
                                
                
                                print("Temporary user created:", temporary_user)

                                request.session['guest_user_data'] = {
                                    'username': temporary_username,
                                    'password': temporary_password,
                                    'email': temporary_user.email,
                                }  
                                
                                print("Username:", request.session['guest_user_data']['username'])
                                print("Password:", request.session['guest_user_data']['password'])
                                print("Email:", request.session['guest_user_data']['email'])

                                user = authenticate(request, username=temporary_username, password=temporary_password)
                                first_name = request.POST.get('first_name')

                                # if guest user is authenticated send email for temporary account
                                if user:
                                    send_temporary_account_email(user, first_name, temporary_username,
                                                                 temporary_password)

                            else:
                                print("Temporary username is null or empty. Handle accordingly.")
                    
            else:
                print(shipping_form.errors)
                return render(request, "cart/shop-checkout.html", {
                'error_message': 'The address form is not valid. Please correct the errors and try again.',
            })

        # Store and calculate order payments
        ordered_items = {}
        for order in orders:
            ordered_items[order] = OrderItem.objects.filter(order=order).select_related('product')
            
            print(f'{order} initial cod = {order.cod_amount}')
            print(f'{order} subtotal = {order.subtotal}')
            print(f'{order} shipping = {order.shipping_fee}')
            
            if order.shipping_fee != 0 and order.discount == 0:
                if order.cod_amount != 0 and order.cod_amount != order.subtotal:
                    order.discount = (order.subtotal + Decimal(order.shipping_fee)) - order.cod_amount
                    print(f'{order} discount calculated  = {order.discount}')
                else:
                    print(f'{order} discount remains  = {order.discount}')
                    
            order.cod_amount = order.subtotal + Decimal(order.shipping_fee) - order.discount
            orders_subtotal += order.subtotal
            total_discount += order.discount
            total_shipping += Decimal(order.shipping_fee)
            print(f'{order} cod = {order.cod_amount}')
            order.save()
        
        total_payment = orders_subtotal + total_shipping - total_discount
        print(f'Total Payment: {total_payment}')
        print(f'Total Discount: {total_discount}')
        print(f'Orders are: {orders}')

        if user.is_authenticated:
            current_user = user
        else:
            current_user = "anonymoususer"
        
        if 'bundle_order' in request.session:
            del request.session['bundle_order']
                
        if request.is_ajax():
            response_data = {
                'isAuthenticated': user.is_authenticated,
                'id': shipping_address.id,
                'email': request.POST.get('email'),
                'firstName': shipping_address.first_name,
                'lastName': shipping_address.last_name,
                'phone': shipping_address.phone,
                'line1': shipping_address.line1,
                'province': shipping_address.province,
                'city': shipping_address.city,
                'barangay': shipping_address.barangay,
                'postcode': shipping_address.postcode,
                'orders': updated_orders,
                'total_shipping': total_shipping,
                'total_payment': total_payment,
            }
            
            return JsonResponse(response_data)
        else:
            context = {
                'orders': orders, 
                'ordered_items': ordered_items,
                'orders_subtotal': orders_subtotal,
                'total_shipping': total_shipping,
                'total_discount': total_discount,
                'total_payment': total_payment,
                'shipping_form': shipping_form,
                'is_authenticated': user.is_authenticated,
                'default_address': default_address,
                'customer_addresses': customer_addresses,
                'title': title,
                'user': user,
                'current_user': current_user,
                'referred_by': referred_by,
            }
            print(f'is_authenticated: {user.is_authenticated}')
            return render(request, "cart/shop-checkout.html", context)
    except Order.DoesNotExist:
        return redirect('home_view')
    except Http404:
        return redirect('home_view')  
    except Exception as e:
        print(f"Exception in checkout view: {e}")
        return JsonResponse({'error': 'Internal Server Error'}, status=500)


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
        orders = Order.objects.filter(user=user, complete=False)

        # Update the shipping address for each incomplete order
        for order in orders:
            order.shipping_address = selected_address
            order.save()
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
    
###################
# Bundle Checkout #
###################

class BundleCheckoutView(View):
    title = "Bundle Checkout"
    template_name = 'cart/shop-bundle-checkout.html'
    
    def get(self, request, *args, **kwargs):
        order_id = request.session['bundle_order']
        order = Order.objects.get(order_id=order_id)
        default_address = order.shipping_address
        ordered_items = OrderItem.objects.filter(order=order).select_related('product').order_by('-product__customer_price')
        order.discount = order.subtotal + Decimal(order.shipping_fee) - order.cod_amount
        order.save()
        
        context = {
            'title': self.title,
            'order': order,
            'default_address': default_address,
            'ordered_items': ordered_items,
            }
        return render(request, self.template_name, context)

    
######################### 
# Set Order to Complete #
#########################

def submit_checkout(request):
    # Check if the session contains a 'bundle_order'
    if "bundle_order" in request.session:
        # Retrieve the bundle order using the order_id from the session
        order_id = request.session['bundle_order']
        order = Order.objects.get(order_id=order_id)
        order.complete = True
        order.save()

        # Store the sponsor in the session if the user was referred by someone
        if order.user.sponsor:
            request.session['referrer'] = order.user.sponor
        else:
            request.session['referrer'] = None
        print("Order is a bundle")
    else:
        # If it's not a bundle order, handle regular checkout orders
        order_ids = request.session.get('checkout_orders', [])
        orders = Order.objects.filter(id__in=order_ids)
        referrer_username = ""
        referrer = None

        print(f'Order in Submit Checkout: {orders}')

        # If the request method is POST, handle the form submission
        if request.method == 'POST':
            # Get the referrer's username from the POST data
            referrer_username = request.POST.get('username')

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

            # Update the referrer and mark each order as complete
            for order in orders:
                order_user = order.user
                order_user.sponsor = referrer_username
                order_user.save()
                order.complete = True
                order.save()
                print(f'Order {order} saved!')

    # Redirect the user to the checkout complete page after processing the orders
    return redirect('cart:checkout_complete')



#########################################################  
#------------------checkout is done---------------------#
######################################################### 

def checkout_done_view(request): 
    title = "Checkout Done"
    username = ""
    email = ""
    password = ""
    
    try:
        # Set session for first time orders
        request.session['new_guest_user'] = True
        request.session['has_existing_order'] = True

        # Delete session and store another for checkout viewing
        if 'bundle_order' in request.session:
            request.session['checkout_done_bundle'] = request.session['bundle_order']
            del request.session['bundle_order']
        
        if 'checkout_orders' in request.session:
            request.session['checkout_done_view'] = request.session.get('checkout_orders', [])
            del request.session['checkout_orders']
            
        orders = []
        ordered_items = {}

        # Register the orders in the variable
        if 'checkout_done_bundle' in request.session and 'checkout_done_view' in request.session:
            order_ids = [request.session['checkout_done_bundle']] + request.session.get('checkout_done_view', [])
            orders = Order.objects.filter(order_id__in=order_ids)
        elif 'checkout_done_bundle' in request.session:
            order_id = request.session['checkout_done_bundle']
            order = Order.objects.get(order_id=order_id)
            orders = [order]
        elif 'checkout_done_view' in request.session:
            order_ids = request.session.get('checkout_done_view', [])
            orders = Order.objects.filter(id__in=order_ids)
        
        # Process orders and order items
        for order in orders:
            ordered_items[order] = OrderItem.objects.filter(order=order).select_related('product').order_by('-product__customer_price')
            order.save()

        print(f'Orders: {orders}')

        # for displaying the temporary username and password
        if request.user.is_anonymous:
            guest_user_info = request.session.get('guest_user_data', {})
            username = guest_user_info.get('username', '')
            password = guest_user_info.get('password', '')
            email = guest_user_info.get('email', '')
            
            print(f'username: {username}, email: {email}, password: {password}')
            
        orders_subtotal = sum(order.subtotal for order in orders)
        total_shipping = sum(Decimal(order.shipping_fee) for order in orders)
        total_payment = sum(order.cod_amount for order in orders)
        
        if request.is_ajax():
            response_data = {
                "username": username,
                "email": email,
                "password": password,
            }
            print("Response:", response_data)
            return JsonResponse(response_data)
        else:
            context = {
                "orders": orders,
                'ordered_items': ordered_items,
                "orders_subtotal": orders_subtotal,
                "username": username,
                "email": email,
                "password": password,
                "title": title,
                "total_payment": total_payment,
            }
            return render(request, "cart/shop-checkout-complete.html", context)
    except Order.DoesNotExist:
        print("Order not found")
        return JsonResponse({"error": "Order not found"}, status=404)
    except Exception as e:
        print(f"Exception in checkout_done_view: {e}")
        return JsonResponse({"error": "An error occurred"}, status=500)

    

def set_order_id_session_variable(request):
    if request.method == 'POST' and request.is_ajax():
        order_id = request.POST.get('order_id')
        request.session['clicked_order_id'] = order_id
        print(f'Order ID: {order_id}')
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

