from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.views import View
from django.views.generic import TemplateView
from django.db import transaction
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

from products.models import Product
from orders.models import *
from addresses.forms import AddressForm
from .utils import sf_calculator

import json


User = get_user_model()

class CartView(TemplateView):
    template_name = 'cart/shop-cart.html'
    title = "Cart"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        referrer_id = self.request.session.get('referrer')
            
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
            'referrer_id': referrer_id,
        })
        
        return context
        
    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')

        # Check if the username exists in the database
        try:
            referrer = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Referrer username does not exist!!'}, status=400)

        # If the username exists, save it to the session
        request.session['referrer'] = username

        return JsonResponse({'success': True})
    

@transaction.atomic
def updateItem(request):
    bundleDetails = json.loads(request.GET.get('bundleDetails', '{}'))
    productId = request.GET.get('productId')
    action = request.GET.get('action')
    quantity = int(request.GET.get('quantity', 1))
    cart_items = 0
    supplier = None
    
    user = request.user
    session_key = request.session.session_key
    
    print(f'Products for sales funnel: {bundleDetails}')
    
    if not session_key:
        request.session.save()
        session_key = request.session.session_key
    
    print('Action: ', action)
    print('Product: ', productId)
    print('Quantity: ', quantity)
    
    try:
        if bundleDetails:
            order_id = request.session['bundle_order']
            order = Order.objects.get(order_id=order_id)
            
            print(f'Order in UpdateItem: {order}')
            
            for productId in bundleDetails.get('productIds', []):
                product = get_object_or_404(Product, id=productId)
                print(productId)
                print('Product: ', productId)
                
                orderItem, order_item_created = OrderItem.objects.get_or_create(order=order, product=product)
                
                orderItem.quantity = 1
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
        
            orderItem, order_item_created = OrderItem.objects.get_or_create(order=order, product=product)
            orderItem.save()
            
            if action == 'add':
                orderItem.quantity += quantity
            elif action == 'minus':
                orderItem.quantity -= quantity
                
            if action == 'remove' or orderItem.quantity <= 0:
                orderItem.delete()
            else:
                orderItem.save()
                
                
            if order.orderitem_set.all().count() == 0:
                order.delete()
        
        print(order)
        print(orderItem)
        print(orderItem.quantity)
        
        existing_orders = Order.objects.filter(user=user, supplier=supplier, complete=False) if user.is_authenticated else \
                        Order.objects.filter(session_key=session_key, supplier=supplier, complete=False)
        
        ordered_items = {}
        for order in existing_orders:
            ordered_items[order] = OrderItem.objects.filter(order=order).select_related('product')
            
        if user.is_authenticated:
            orders = Order.objects.filter(user=user, complete=False)
        else:
            orders = Order.objects.filter(session_key=session_key, complete=False)
        
        request.session['checkout_orders'] = list(orders.values_list('id', flat=True))
            
        cart_items = sum(order.total_quantity for order in orders)
        total_cart_subtotal = sum(order.calculate_subtotal() for order in orders)
        
        print(f'total items in cart: {cart_items}')
        
        return JsonResponse({
            'action': action,
            'cart_items': cart_items,
            'total_cart_subtotal': total_cart_subtotal,
            'products': [{
                'id': product.id,
                'name': product.name,
                'image': getattr(product.image_1, 'url', None) if product.image_1 else None,
                'quantity': orderItem.quantity,
                'total': orderItem.get_total,
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
    is_authenticated = False
    default_address = ""
    ordered_items = []
    temporary_username = ""
    temporary_password = ""
    customer_addresses = ""
    shipping_fee = 0.00
    orders_subtotal = Decimal('0.00')
    total_shipping = Decimal('0.00')
    
    referrer = request.session.get('referrer')
    print(f'Referred ID: {referrer}')
    user = request.user
    session_key = request.session.session_key

    try:
        is_authenticated = request.user.is_authenticated
        
        if is_authenticated:
            is_authenticated = True
            default_address = Address.objects.filter(user=user, is_default=True).first()
            # orders = Order.objects.filter(user=user, complete=False)
            customer_addresses = Address.objects.filter(user=user).exclude(is_default=True).order_by('-is_default')[:3]
        # else:
        #     orders = Order.objects.filter(user=None, session_key=session_key, complete=False)
            
        order_ids = request.session.get('checkout_orders', [])
        orders = Order.objects.filter(id__in=order_ids)
        
        if default_address:
            region = default_address.region
            print(f"Shipping Fee: {shipping_fee}")
            print(f"Address Region: {region}")
            for order in orders:
                order.shipping_address = default_address
                qty = order.total_quantity
                shipping_fee = sf_calculator(region=region, qty=qty)
                order.shipping_fee = shipping_fee
                order.save()
                
        
        for order in orders:        
            with transaction.atomic():
                existing_order_items = order.orderitem_set.all()
                print("Order items:", order.orderitem_set.all())
                for order_item in existing_order_items:
                    product = order_item.product
                    ordered_items.append(OrderItem(order=order, product=product, quantity=order_item.quantity))   
                order.save()
        
        if request.method == 'POST':  
            shipping_form = AddressForm(request.POST)
            
            if shipping_form.is_valid():
                shipping_address = shipping_form.save(commit=False)
                
                region = shipping_form.cleaned_data.get('region')
                for order in orders:
                    qty = order.total_quantity
                    shipping_fee = sf_calculator(region=region, qty=qty)
                    order.shipping_fee = shipping_fee
                    order.save()
                    
                updated_orders = [{'id': order.id, 'shipping_fee': order.shipping_fee} for order in orders]
                
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
                                        referrer_user = User.objects.get(username=referrer)
                                        temporary_user.referred_by = referrer_user
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
                                name = request.POST.get('first_name')
                                
                                if user: 
                                    subject = 'TWC Online Store Temporary Account'
                                    message = f'Good Day {name},\n\n\nYou have successfully registered an account on TWConline.store!!\n\n\nHere are your temporary account details:\n\nUsername: {temporary_username}\nPassword: {temporary_password}\n\n\nThank you for your order!'
                                    from_email = settings.EMAIL_MAIN
                                    recipient_list = [temporary_user.email]
                                    
                                    try:
                                        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                                        print("Email sent successfully!")
                                    except Exception as e:   
                                        print(f"Error sending email: {e}")
                                
                            else:
                                print("Temporary username is null or empty. Handle accordingly.")
                    
            else:
                print(shipping_form.errors)
                return render(request, "cart/shop-checkout.html", {
                'error_message': 'The address form is not valid. Please correct the errors and try again.',
            })
        #put order display here
                        
        ordered_items = {}
        for order in orders:
            ordered_items[order] = OrderItem.objects.filter(order=order).select_related('product')
            orders_subtotal += order.subtotal
            total_shipping += Decimal(order.shipping_fee)
        
        total_payment = orders_subtotal + total_shipping
        print(f'Total Payment: {total_payment}')
        print(f'Orders are: {orders}')
                
        if request.is_ajax():
            response_data = {
                'isAuthenticated': is_authenticated,
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
                'total_payment': total_payment,
                'shipping_form': shipping_form,
                'is_authenticated': is_authenticated,
                'default_address': default_address,
                'customer_addresses': customer_addresses,
                'title': title,
            }
            print(f'is_authenticated: {is_authenticated}')
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
    print("Incoming GET request to 'get-selected-address'")
    if request.method != 'GET':
        return JsonResponse({'success': False, 'error': 'Invalid request method.'})

    selected_address_id = request.GET.get('selected_address_id')
    print(f"selected address: {selected_address_id}")
    if not selected_address_id:
        return JsonResponse({'success': False, 'error': 'Missing address ID.'})

    try:
        selected_address = get_object_or_404(Address, pk=selected_address_id)
        print(selected_address.barangay)
    except Http404:
        return JsonResponse({'success': False, 'error': 'Address not found.'})
    
    try:
        user=request.user
        orders = Order.objects.filter(user=user, complete=False)
        
        for order in orders:
            order.shipping_address = selected_address
            order.save()
    except Exception as e:
        print(f"Exception in checkout view: {e}")
        return JsonResponse({'error': 'Internal Server Error'}, status=500)
            
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
    
        discount = order.subtotal + Decimal(order.shipping_fee) - order.cod_amount
        order.discount = discount
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
    
    if "bundle_order" in request.session:
        order_id = request.session['bundle_order']
        order = Order.objects.get(order_id=order_id)
        order.complete = True
        order.save()
        
        request.session['referrer'] = order.user.referred_by.username
    else:
        order_ids = request.session.get('checkout_orders', [])
        orders = Order.objects.filter(id__in=order_ids)
    
        if request.method == 'POST':
            referrer_username = request.POST.get('username')
            request.session['referrer'] = referrer_username
            referrer = None
            
            if referrer_username:
                try:
                    referrer = User.objects.get(username=referrer_username)
                except User.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'Referrer username does not exist'}, status=400)
            
            for order in orders:
                order_user = order.user
                order_user.referred_by = referrer
                order_user.save()
                order.complete = True
                order.save()
        
    return redirect('cart:checkout_complete')

#########################################################  
#------------------checkout is done---------------------#
######################################################### 

def checkout_done_view(request): 
    title = "Checkout Done" 
    username = ""
    email = ""
    password = ""
    referrer = ""
    ordered_items = {}
    
    try:
        referrer = request.session['referrer']
        request.session['new_guest_user'] = True
        request.session['has_existing_order'] = True
        
        print(request.session)
        
        if 'bundle_order' in request.session:
            request.session['checkout_done_bundle'] = request.session['bundle_order']
            del request.session['bundle_order']
        
        if 'checkout_orders' in request.session: 
            request.session['checkout_done_view'] = request.session.get('checkout_orders', [])
            del request.session['checkout_orders']
            
        orders = []

        if 'checkout_done_bundle' in request.session:
            order_id = request.session['checkout_done_bundle']
            order = Order.objects.get(order_id=order_id)
            orders = [order]
            ordered_items[order] = OrderItem.objects.filter(order=order).select_related('product').order_by('-product__customer_price')
        else:
            order_ids = request.session.get('checkout_done_view', [])
            orders = Order.objects.filter(id__in=order_ids)
            
            ordered_items = {}
            for order in orders:
                ordered_items[order] = OrderItem.objects.filter(order=order).select_related('product')
                order.save()
        
        if request.user.is_anonymous:
            
            guest_user_info = request.session.get('guest_user_data', {})
            username = guest_user_info.get('username')
            password = guest_user_info.get('password')
            email = guest_user_info.get('email')
            
            print(f'username: {username}, email: {email}, password: {password}')
            
        orders_subtotal = sum(order.subtotal for order in orders)
        total_shipping = sum(Decimal(order.shipping_fee) for order in orders)
        if 'checkout_done_bundle' in request.session:
            total_payment = sum(order.cod_amount for order in orders)
        else:
            total_payment = orders_subtotal + total_shipping
        

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
                "referrer": referrer,
                "title": title,
                "total_payment": total_payment,
            }
            return render(request, "cart/shop-checkout-complete.html", context)
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

