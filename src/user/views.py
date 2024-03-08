from django.views.generic import View, TemplateView
from django.views.generic.edit import FormView
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from orders.models import Order, OrderItem
from addresses.models import Address
from user.utils import get_or_create_customer
from django.utils import timezone
from django.urls import reverse
from billing.models import Customer
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.conf import settings
from django.views.decorators.cache import cache_page
from user.forms import ProfileForm, ProfilePictureForm
from addresses.forms import AddressForm
from django.db.models import Sum, Q


import logging

User = get_user_model()

@cache_page(60 * 15)
def get_order_details(request):
    logger = logging.getLogger(__name__) 
    if request.method == 'GET':
        order_id = request.GET.get('order_id')
        if order_id:
            order = get_object_or_404(Order, order_id=order_id)
            order_items = order.orderitem_set.select_related('product')

            data = {
                'order_id': order.order_id,
                'created_at': order.created_at.strftime("%Y-%m-%d"),
                'total_amount': sum([item.get_total for item in order_items]),
                'total_quantity': sum([item.quantity for item in order_items]),
                'status': order.status,
                'order_items': [
                    {
                        'product_name': item.product.name,
                        'quantity': item.quantity,
                        'price': item.get_total,
                    } for item in order_items
                ]
            }
            print(data)
            return JsonResponse(data)
        else:
            return HttpResponseBadRequest("Order ID is required")
    else:
        return HttpResponseBadRequest("Only GET method is allowed")
    
    
def update_address(request):
    if request.method == 'POST':
        # Retrieve data from POST request
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
    
    
def get_address_details(request):
    if request.method == 'GET':
        address_id = request.GET.get('address_id')
        try:
            address = Address.objects.get(pk=address_id)
            # Serialize address data as needed
            address_data = {
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


def delete_address(request):
    if request.method == "POST" and request.is_ajax():
        address_id = request.POST.get("address_id")
        try:
            address = Address.objects.get(id=address_id)
            address.delete()
            return JsonResponse({"message": "Address deleted successfully."}, status=200)
        except Address.DoesNotExist:
            return JsonResponse({"error": "Address not found."}, status=404)
    else:
        return JsonResponse({"error": "Invalid request."}, status=400)


class DashboardView(TemplateView):
    template_name = 'user/dashboard.html'
    title = "User Dashboard"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = ""
        order = ""
        
        if self.request.user.is_authenticated:
            customer, created = Customer.get_or_create_customer(self.request.user, self.request)
            order = Order.objects.filter(customer=customer, complete=True)
            pending_orders = order.filter(
                    Q(complete=False) | ~Q(status='received')
                )
            completed_orders = Order.objects.filter(customer=customer, complete=True, status='received')
            pending_orders_count = pending_orders.count()
            completed_order_count = completed_orders.count()
                
                    
        context = {
            'title': self.title,
            'customer': customer,
            'orders': order,
            'addresses': Address.objects.filter(customer=customer),
            'ordered_items': OrderItem.objects.filter(order=order),
            'pending_orders_count': pending_orders_count,
            'completed_order_count': completed_order_count,
            'profile_form': ProfileForm(instance=self.request.user),
        }
        
        return context
    
    def post(self, request, *args, **kwargs):
        current_user = User.objects.get(id=request.user.id) 
        profile_form = ProfileForm(request.POST, request.FILES, instance=current_user)
        address_form = AddressForm(request.POST)
        
        if address_form.is_valid():
            address = address_form.save(commit=False)
            address.customer = request.user.customer
            address.save()
            return HttpResponseRedirect(reverse('dashboard'))
        else:
            print("Address form is invalid.")
            print("Address form is invalid:", address_form.errors)
        
        if profile_form.is_valid():
            profile_form.save()      
            return HttpResponseRedirect(reverse('dashboard'))
        else:
            print("Profile form is invalid.")
            print("Profile form errors:", profile_form.errors)

        return self.render_to_response(self.get_context_data())

    
class SellerDashboardView(TemplateView):
    template_name = 'seller/seller-dashboard.html'
    title = "Seller Dashboard"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_seller:
            return redirect('home_view')
        elif not request.user.is_seller:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        customer, created = Customer.get_or_create_customer(self.request.user, self.request)
        referred_users = User.objects.filter(referred_by=user)
            
        if not customer:
            customer = get_or_create_customer(self.request)      
        affiliate_link = self.request.user.generate_affiliate_link()
    

        context.update({
            'title': self.title,
            'customer': customer,
            'orders': Order.objects.filter(customer=customer),
            'addresses': Address.objects.filter(customer=customer),
            'affiliate_link': affiliate_link,
            'referred_users': referred_users, 
        })
        return context
    
    def post(self, request, *args, **kwargs):
        profile_form = ProfileForm(request.POST, instance=request.user)
        if profile_form.is_valid():
            profile_form.save()
            print("Profile form is valid. Saving profile...")
            return redirect('seller_dashboard')
        else:
            print("Profile form is invalid. Errors:", profile_form.errors)
        
        return self.get(request, *args, **kwargs)
        

class RegisterGuestView(View):
    def get(self, request, *args, **kwargs):
        # Store the referrer_id in the session
        request.session['referrer_id'] = kwargs['referrer_id']
        # Mark the session as modified to make sure it gets saved
        request.session.modified = True
        # Redirect to the dashboard
        return HttpResponseRedirect(f'http://{settings.SITE_DOMAIN}/')
    

    
