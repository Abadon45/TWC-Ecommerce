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
from addresses.forms import AddressForm


User = get_user_model()

class CartView(TemplateView):
    template_name = 'cart/shop-cart.html'
    title = "Cart"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context

@transaction.atomic
def updateItem(request):
    productId = request.GET.get('productId')
    action = request.GET.get('action')
    quantity = int(request.GET.get('quantity', 1))
    
    user = request.user
    session_key = ""
    
    print('Action: ', action)
    print('Product: ', productId)
    print('Quantity: ', quantity)
    
    try:
        
        print('User ID:', request.user.id)
        if user.is_authenticated:
            print(f"User is authenticated: {user.username}")
            order = Order.objects.filter(user=user, complete=False).first()
            
        else:
            print(f"User is not authenticated")
            session_key = request.session.session_key
            order, created = Order.objects.get_or_create(session_key=session_key, complete=False)
            
        if not order:
            if user.is_authenticated:
                order = Order.objects.create(user=user)
            else:
                order = Order.objects.create(session_key=session_key)
        
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
            
        total_quantity = order.orderitem_set.aggregate(Sum('quantity'))['quantity__sum']
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
    

#----------------- Checkout Views -------------------

def checkout(request):
    title = "Checkout"
    shipping_form = AddressForm()
    order = Order()
    is_authenticated = False
    default_address = ""
    ordered_items = []
    order_dict = []
    temporary_username = ""
    temporary_password = ""
    customer_addresses = ""  
    
    referrer_id = request.session.get('referrer')
    user = request.user
    session_key = ""

    try:
        is_authenticated = request.user.is_authenticated
        
        if is_authenticated:
            is_authenticated=True
            user = request.user
            default_address = Address.objects.filter(user=user, is_default=True).first()
            order = Order.objects.filter(user=user, complete=False).first()
            customer_addresses = Address.objects.filter(user=user).exclude(is_default=True).order_by('-is_default')[:3]      
        else:
            session_key = request.session.session_key
            order = Order.objects.filter(session_key=session_key, complete=False).first()
        
            if not order:
                return redirect('cart:cart')
        
        if default_address:
            print(f"Default Address: {default_address}")
            order.shipping_address = default_address
            order.save()
                
        if order:
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
                print(shipping_address.session_key)
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
                                temporary_password = User.objects.make_random_password(length=6)
                                
                                if referrer_id:
                                    try:
                                        referrer = User.objects.get(id=referrer_id)
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
                return render(request, "cart/shop-checkout.html", {
                'error_message': 'The address form is not valid. Please correct the errors and try again.',
            })
            

                
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
            }
            return JsonResponse(response_data)
        else:
            context = {
                'order': order_dict,
                'shipping_form': shipping_form,
                'is_authenticated': is_authenticated,
                'default_address': default_address,
                'customer_addresses': customer_addresses,
                'title': title,
            }
            print(f'is_authenticated: {is_authenticated}')
            return render(request, "cart/shop-checkout.html", context)
    except Http404:
        return redirect('cart:cart')
        
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
        order, order_created = Order.objects.get_or_create(user=user, complete=False)
        
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


#########################################################  
#------------------checkout is done---------------------#
######################################################### 

def checkout_done_view(request): 
    title = "Checkout Done" 
    username = ""
    email = ""
    password = ""
    user  = request.user
    
    try:
        request.session['new_guest_user'] = True
        request.session['has_existing_order'] = True
        if request.user.is_authenticated:
            order = Order.objects.filter(user=user, complete=False).first()    
        elif request.user.is_anonymous:
            session_key = request.session.session_key
            order = Order.objects.filter(session_key=session_key, complete=False).first() 
            print(f"Guest User: {session_key}")
            
            guest_user_info = request.session.get('guest_user_data', {})
            username = guest_user_info.get('username')
            password = guest_user_info.get('password')
            email = guest_user_info.get('email')
            
            print(f'username: {username}, email: {email}, password: {password}')

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
                    "username": username,
                    "email": email,
                    "password": password,
                    "title": title,
                }
                return render(request, "cart/shop-checkout-complete.html", context)
        else:
            print("No incomplete order found for this customer")
            if user.is_authenticated:
                completed_order = Order.objects.filter(user=user, complete=True).order_by("-created_at").first()
            else:
                completed_order = Order.objects.filter(session_key=session_key, complete=True).first()
            print(completed_order)
            print(f"Completed Order ID: {completed_order.order_id}")

            if completed_order:
                ordered_items = OrderItem.objects.filter(order=completed_order)

                print("Ordered Items:", ordered_items)
                total_quantity = sum(item.quantity for item in ordered_items)
                total_amount = sum(item.get_total for item in ordered_items)
                order_data = {
                    "order_id": completed_order.order_id,
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
                    "username": username,
                    "email": email,
                    "password": password,
                    "title": title,
                }
                return render(request, "cart/shop-checkout-complete.html", context)
            else:
                return redirect('home_view')
    except Exception as e:
        print(f"Exception in checkout_done_view: {e}")

        return JsonResponse({"error": "An error occurred"}, status=500)
