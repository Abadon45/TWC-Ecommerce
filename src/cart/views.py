from user.utils import create_or_get_guest_user
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import Http404
from django.views.generic import TemplateView
from django.db import transaction
from django.db.models import Sum
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings

from products.models import Product
from orders.models import *
from billing.models import Customer
from addresses.forms import AddressForm


User = get_user_model()

class CartView(TemplateView):
    template_name = 'cart/shop-cart.html'


def updateItem(request):
    productId = request.GET.get('productId')
    action = request.GET.get('action')
    quantity = int(request.GET.get('quantity', 1))
    
    user = request.user
    
    print('Action: ', action)
    print('Product: ', productId)
    print('Quantity: ', quantity)
    
    try:
        
        print('User ID:', request.user.id)
        if user.is_authenticated:
            print(f"User is authenticated: {user.username}")
            customer, created = Customer.objects.get_or_create(user=user, defaults={'email': user.email})
            customer.save()
            
        else:
            print(f"User is not authenticated")
            customer = create_or_get_guest_user(request)
        
        print(customer)
        
        order = Order.objects.filter(customer=customer, complete=False).first()
        
        if not order:
            order = Order.objects.create(customer=customer)
        
        product = get_object_or_404(Product, id=productId)
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
        
        print(order)
        print(orderItem)
        print(orderItem.quantity)
            
        # Store anonymous order ID in session if the user is a guest
        if not request.user.is_authenticated:
            anonymous_orders = request.session.get('anonymous_orders', [])
            anonymous_orders.append(order.id)
            request.session['anonymous_orders'] = anonymous_orders
            print(request.session.get('anonymous_orders', []))
    
        total_quantity = OrderItem.objects.filter(order__customer=customer, order__complete=False).aggregate(Sum('quantity'))['quantity__sum']
        cart_items_count = total_quantity if total_quantity is not None else 0
 
        return JsonResponse({
            'cart_items': cart_items_count,
            'products': [{
                'id': product.id,
                'name': product.name,
                'image': getattr(product.image_1, 'url', None) if product.image_1 else None,
                'quantity': orderItem.quantity,
                'total': orderItem.get_total,
            }],
            'action': action
        }, safe=False)
        
    except Exception as e:
        print(f"Exception in updateItem: {e}")
        return JsonResponse({'error': 'Internal Server Error'}, status=500)
    
    
# ---------------  Update Address Views -------------- 

# def get_address(request):
#     address_id = request.GET.get('id')
#     address = Address.objects.get(id=address_id)  # Assuming you have an Address model
#     print(f'address: {address}')
#     return render(request, 'cart/address_fragment.html', {'address': address})

# def update_selected_address(request):
#     if request.method == "POST":
#         data = json.loads(request.body)  # Extract name and addressLine
#         request.session['selected_address'] = data
#         return JsonResponse({'success': True}) 
#     else:
#         return HttpResponseBadRequest() 

# def refresh_checkout_address(request):
#     # Retrieve data from the session if 'selected_address' exists
#     selected_address = request.session.get('selected_address') 
#     print(selected_address)
#     return render(request, 'cart/checkout_address_snippet.html', {'address': selected_address})


#note: default address should be displayed_address = request.GET.get('default_address') or it should be ID
#      and selected address should be displayed_address = request.GET.get('selected_address')
#      it should be fetched on an address so that it would be dynamic and the id should be posted on /get-address/?id={{ address.id }}


#----------------- Checkout Views -------------------

def checkout(request):
    shipping_form = AddressForm()
    order = Order()
    is_authenticated = False
    default_address = ""
    ordered_items = []
    order_dict = []
    order_id = ""
    temporary_username = ""
    temporary_password = ""
    
    referrer_id = request.session.get('referrer')

    try:
        user = request.user
        is_authenticated = request.user.is_authenticated
        if is_authenticated:
            is_authenticated=True
            customer = get_object_or_404(Customer, user=user)
            default_address = Address.objects.filter(customer=customer, is_default=True).first()
            
        elif user.is_anonymous:
            customer = create_or_get_guest_user(request)
            
                
            subtotal = order.get_cart_items
            order_dict = {
                'get_cart_total': 0, 
                'subtotal': subtotal, 
                'shipping': False
            }  
        
        if customer is None:
            return redirect('cart:cart')
        
        #get or create order for the current customer     
        order, order_created = Order.objects.get_or_create(customer=customer, complete=False)
        if order_created:
            order_id = order.order_id
            print(f"Order created: {order_created}")
            
        if default_address:
            print(f"Default Address: {default_address}")
            order.shipping_address = default_address
            order.save()
                
        if customer:
            order = get_object_or_404(Order, customer=customer, complete=False)
            with transaction.atomic():
                existing_order_items = order.orderitem_set.all()
                for order_item in existing_order_items:
                    product = order_item.product
                    ordered_items.append(OrderItem(order=order, product=product, quantity=order_item.quantity))   
                order.save()
        
        if customer.id:
            customer_addresses = Address.objects.filter(customer=customer).exclude(is_default=True).order_by('-is_default')[:3]
                
        if request.method == 'POST':  
            if customer is not None:      
                shipping_form = AddressForm(request.POST)
                
                if shipping_form.is_valid():
                    shipping_address = shipping_form.save(commit=False)
                    shipping_address.customer = customer
                    shipping_address.save()
                    
                    
                    if not Address.objects.filter(customer=customer, is_default=True).exists():
                        # If not, set the new address as the default
                        shipping_address.is_default = True
                        shipping_address.save()
                    
                    print("Shipping address created:", shipping_address)                   
                    if not order.shipping_address:
                        
                        order.shipping_address = shipping_address
                        order.contact_number = shipping_address.phone
                        order.save()
                    
                        print("Order Information After Address Update:", order.order_id, order.shipping_address)
                        
                        #Generate a temporary account for the Guest User
                        if request.user.is_anonymous:
                            temporary_username = request.POST.get('username').lower()  
                            print(f'username retrieved from ajax: {temporary_username}') 
                                    
                            if temporary_username:
                                print("Creating temporary user...")
                                temporary_user, user_created = User.objects.get_or_create(username=temporary_username)
                                if user_created:
                                    print(f"User created: {user_created}")
                                    temporary_password = User.objects.make_random_password()
                                    
                                    if referrer_id:
                                        try:
                                            referrer = User.objects.get(id=referrer_id)
                                            temporary_user.referred_by = referrer
                                            temporary_user.save()
                                        except User.DoesNotExist:
                                            print("Referrer not found.")
                                    
                                    # PUT THIS ON THE FINAL VERSION
                                    # if User.objects.filter(email=customer.email).exists():
                                    #     print("A user with this email already exists.") 
                                    # else:
                                    
                                    
                                    #---------------------------------------
                                    # Transfer Details to the temporary_user
                                    #---------------------------------------
                                    customer.email = request.POST.get('email')
                                    temporary_user.email = customer.email
                                    temporary_user.set_password(temporary_password)
                                    temporary_user.first_name = shipping_address.first_name
                                    temporary_user.last_name = shipping_address.last_name
                                    temporary_user.mobile = shipping_address.phone
                                    temporary_user.save()
                                    customer.user = temporary_user
                                    customer.save()
                                    
                                    
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
                    return render(request, "cart/shop-checkout.html", {
                    'error_message': 'The address form is not valid. Please correct the errors and try again.',
                })
            else:
                customer = create_or_get_guest_user(request) 
                return redirect('cart:cart')
            
        if request.is_ajax():
            response_data = {
                'isAuthenticated': is_authenticated,
                'email': customer.email,
                'firstName': shipping_address.first_name,
                'lastName': shipping_address.last_name,
                'phone': shipping_address.phone,
                'line1': shipping_address.line1,
                'province': shipping_address.province,
                'city': shipping_address.city,
                'barangay': shipping_address.barangay,
                'postcode': shipping_address.postcode,
            }
            return JsonResponse(response_data)
        else:
            context = {
                'order_id': order_id,
                'order': order_dict,
                'shipping_form': shipping_form,
                'is_authenticated': is_authenticated,
                'default_address': default_address,
                'customer_addresses': customer_addresses,
            }
            print(f'is_authenticated: {is_authenticated}')
            return render(request, "cart/shop-checkout.html", context)
    except Http404:
        return redirect('cart:cart')
        
    except Exception as e:
        print(f"Exception in checkout view: {e}")
        return JsonResponse({'error': 'Internal Server Error'}, status=500)
    

def checkout_done_view(request):  
    username = ""
    email = ""
    password = ""
    
    try:
        request.session['new_guest_user'] = True
        if request.user.is_authenticated:
            customer = request.user.customer
            print(f"Customer: {customer}")
            

        elif request.user.is_anonymous:
            customer = create_or_get_guest_user(request)
            print(f"Guest Customer: {customer}")
            
            guest_user_info = request.session.get('guest_user_data', {})
            username = guest_user_info.get('username')
            password = guest_user_info.get('password')
            email = guest_user_info.get('email')
            
            print(f'username: {username}, email: {email}, password: {password}')

        else:
            customer = None
            return redirect("home_view")

        order = Order.objects.filter(customer=customer, complete=False).first()

        if order is not None:
            print(f'Shipping Address: {order.shipping_address}')
            with transaction.atomic():
                existing_order_items = order.orderitem_set.all()
                # Add a method here to calculate the number of products sold
                ordered_items = list(existing_order_items)
                order.complete = True
                existing_order_items.delete()
                OrderItem.objects.bulk_create(ordered_items)

            order.save()

            # Fetch the ordered items associated with the completed order
            ordered_items = OrderItem.objects.filter(order=order)
            total_quantity = sum(item.quantity for item in ordered_items)
            total_amount = sum(item.get_total for item in ordered_items)

            print("Ordered Items:", ordered_items)

            order_data = {
                "order_id": order.order_id,
                "customer": order.customer,
                "shipping_address": order.shipping_address,
                "complete": True,
                "created_at": timezone.now(),
                "ordered_items": ordered_items,
                "total_quantity": total_quantity,
                "total_amount": total_amount,
            }

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
                    "order": order_data,
                    "customer": customer,
                    "username": username,
                    "email": email,
                    "password": password,
                }
                return render(request, "cart/shop-checkout-complete.html", context)
        else:
            print("No incomplete order found for this customer")
            completed_order = (
                Order.objects.filter(customer=customer, complete=True)
                .order_by("-created_at")
                .first()
            )
            print(completed_order)
            print(f"Completed Order ID: {completed_order.order_id}")

            if completed_order:
                ordered_items = OrderItem.objects.filter(order=completed_order)

                print("Ordered Items:", ordered_items)
                total_quantity = sum(item.quantity for item in ordered_items)
                total_amount = sum(item.get_total for item in ordered_items)
                order_data = {
                    "order_id": completed_order.order_id,
                    "customer": completed_order.customer,
                    "shipping_address": completed_order.shipping_address,
                    "complete": True,
                    "created_at": timezone.now(),
                    "ordered_items": ordered_items,
                    "total_quantity": total_quantity,
                    "total_amount": total_amount,
                }
                
                if request.is_ajax():
                    response_data = {
                        "username": username,
                        "email": email,
                        "password": password,
                    }
                    print("Response:", response_data)
                    return JsonResponse(response_data)

                context = {
                    "order": order_data,
                    "customer": customer,
                    "username": username,
                    "email": email,
                    "password": password,
                }
                return render(request, "cart/shop-checkout-complete.html", context)
            else:
                return render(request, "cart/shop-cart.html")
    except Exception as e:
        print(f"Exception in checkout_done_view: {e}")

        return JsonResponse({"error": "An error occurred"}, status=500)


# @receiver(user_logged_in)
# def user_logged_in_handler(request, user, **kwargs):
#     if user.is_staff:
#         return redirect('/admin/')
#     anonymous_orders = request.session.get('anonymous_orders', [])
    
#     print("Anonymous Orders:", anonymous_orders)
    
#     if anonymous_orders:
#         latest_order = Order.objects.filter(id__in=anonymous_orders[1:])
        
#         print("Latest Orders:", latest_order)
        
#         if latest_order.exists():
#             latest_order = latest_order.latest('created_at')

#             print("Latest Order ID:", latest_order.order_id)
#             existing_orders = Order.objects.filter(customer=request.user.customer, complete=False)
#             if existing_orders.exists():
#                 existing_order = existing_orders.latest('created_at')
#                 print("Existing Order ID:", existing_order.order_id)
#                 for item in latest_order.orderitem_set.all():
#                     order_item, created = OrderItem.objects.get_or_create(order=existing_order, product=item.product)
#                     order_item.quantity += item.quantity
#                     order_item.save()

#                 latest_order.delete()

#                 print("Cart items merged successfully.")

#                 messages.success(request, 'Cart items merged successfully.')
#                 return redirect('cart:cart')
#             else:
#                 latest_order.customer = request.user.customer
#                 latest_order.save()

#                 print("Guest order assigned to the authenticated user.")

#                 messages.success(request, 'Guest order assigned to the authenticated user.')
#                 return redirect('home_view')

#     print("No anonymous orders found.")
#     return redirect('home_view')
