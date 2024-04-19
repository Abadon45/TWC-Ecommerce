from django.views.generic import View, TemplateView
from django.contrib.auth.views import LogoutView
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from orders.models import Order, OrderItem, Courier
from addresses.models import Address
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseBadRequest, HttpResponse
from django.conf import settings
from django.views.decorators.cache import cache_page
from user.forms import ProfileForm
from orders.forms import CourierBookingForm
from addresses.forms import AddressForm
from django.db.models import Q
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from decimal import Decimal

import logging
from .utils import fulfiller

logger = logging.getLogger(__name__)



import logging

User = get_user_model()

class RegisterGuestView(View):
    def get(self, request, *args, **kwargs):
        # Store the referrer_id in the session
        request.session['referrer_id'] = kwargs['referrer_id']
        # Mark the session as modified to make sure it gets saved
        request.session.modified = True
        # Redirect to the dashboard
        return HttpResponseRedirect(f'http://{settings.SITE_DOMAIN}/')
    

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
    paginate_by = 10
    
    def get(self, request, *args, **kwargs):
        user = request.user
        clicked_order_id = request.session.get('clicked_order_id')
        print(f"Order ID fetched: {clicked_order_id}")
        logger.debug(f"Session Data: {request.session}") 
        
        if request.user.is_authenticated:
            order = Order.objects.filter(user=user, status='pending', complete=True).order_by('-created_at')
            order = order.prefetch_related('orderitem_set')
            paginator = Paginator(order, self.paginate_by)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            pending_orders_count = order.filter(Q(complete=False) | ~Q(status='received')).count()
            completed_order_count = Order.objects.filter(user=user, complete=True, status='received').count()
            
            
            context = {
                'title': self.title,
                'page_obj': page_obj,
                'order': order,
                'addresses': Address.objects.filter(user=user),
                'ordered_items': OrderItem.objects.filter(order=order),
                'pending_orders_count': pending_orders_count,
                'completed_order_count': completed_order_count,
                'profile_form': ProfileForm(instance=request.user),
            }
            
            if request.is_ajax():
                pagination_html = render_to_string('user/user-order-pagination.html', {'page_obj': page_obj}, request=request)
                orders_data = []
                for order in page_obj.object_list:
                    order_data = {
                        'order_id': order.order_id,
                        'created_at': order.created_at, 
                        'get_cart_items': order.get_cart_items,
                        'status': order.status,
                        'total_amount': order.total_amount,
                    }
                    orders_data.append(order_data)
                response_data = {
                    'pagination_html': pagination_html,
                    'orders': orders_data,
                    'clicked_order_id': clicked_order_id,
                }
                return JsonResponse(response_data)
            else:
                return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        try:
            current_user = User.objects.get(id=request.user.id) 
            profile_form = ProfileForm(request.POST, request.FILES, instance=current_user)
            address_form = AddressForm(request.POST)
            
            if address_form.is_valid():
                address = address_form.save(commit=False)
                address.user = request.user
                address.save()   
            else:
                print("Address form is invalid.")
                print("Address form is invalid:", address_form.errors)
            
            if profile_form.is_valid():
                profile_form.save()      
            else:
                print("Profile form is invalid.")
                print("Profile form errors:", profile_form.errors)

            return HttpResponseRedirect(reverse('dashboard'))
        except Exception as e:
            print(f"Server error is caused by: {e}")
            return JsonResponse({'error': "Invalid request."}, status=500)
        
def dashboard_redirect(request):
    # Redirect to the root URL with the appropriate tab path appended
    return redirect('/')

    
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
        referred_users = User.objects.filter(referred_by=user)
        
        referred_orders = Order.objects.filter(
                Q(user__in=referred_users),
                Q(delivered=False),
                Q(status='pending') | Q(status='for-booking')
            )
        referred_orders_count = referred_orders.count()
        self.request.session['referred_orders_count'] = referred_orders_count
        
        
        affiliate_link = self.request.user.generate_affiliate_link()
    

        context.update({
            'title': self.title,
            'orders': Order.objects.filter(user=user),
            'addresses': Address.objects.filter(user=user),
            'affiliate_link': affiliate_link,
            'referred_users': referred_users, 
            'referred_orders': referred_orders,
            'ordered_items': OrderItem.objects.filter(order=referred_orders),
            'referred_orders_count': referred_orders_count,
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
    
class ReviewOrderView(View):
    http_method_names = ['get']

    template_name = 'seller/review-order.html'
    title = "Review Order"
    
    def get(self, request, order_id, *args, **kwargs):
        try:
            order = Order.objects.get(order_id=order_id, status='pending')
        except Order.DoesNotExist:
            return render(request, '404.html', status=404)
        
        max_profit = order.subtotal - order.seller_total
        
        context = self.get_context_data(request, order=order)
        
        if request.is_ajax():
            data = {
            'order': {
                'id': order.id,
                'order_id': order.order_id,
            },
            'max_profit': max_profit,
        }
        
            return JsonResponse(data)
        else:
            return render(request, self.template_name, context)
    
    def get_context_data(self, request, order, **kwargs):
        referred_orders_count = request.session.get('referred_orders_count')
        transaction_fee = order.distributor_total * Decimal(0.05)
        cod_amount = order.total_amount - order.discount
        max_profit = order.subtotal - order.seller_total
        address = order.shipping_address
        region = address.region
        fulfiller_name = fulfiller(region)
        existing_courier = order.courier

        if existing_courier is None:
            new_courier = Courier.objects.create(fulfiller=fulfiller_name)
            order.courier = new_courier
            
        order.sponsor_profit = order.seller_total - order.distributor_total - transaction_fee
        order.seller_profit = cod_amount - order.seller_total - order.shipping_fee
        order.save()
        
        context = {
            'title': self.title,
            'order': order,
            'referred_orders_count': referred_orders_count,
            'transaction_fee': transaction_fee,
            'cod_amount': cod_amount,
            'max_profit': max_profit,
            'address': address,
        }
        return context
    

def update_discount(request):
    if request.method == 'POST' and request.is_ajax():
        print("Request is POST")
        order_id = request.POST.get('order_id')
        new_discount = request.POST.get('discount')

        print("Order ID:", order_id)
        print("New Discount:", new_discount)
        
        try:
            order = Order.objects.get(order_id=order_id)
            order.discount = new_discount
            order.save()
            return JsonResponse({'success': True, 'discount_amount': order.discount})
        except Order.DoesNotExist:
            print("Order does not exist")
            return JsonResponse({'success': False})
    else:
        print("Invalid request method or not AJAX")
        return JsonResponse({'success': False})
    
def confirm_order(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        payment_method = request.POST.get('payment_method')
        try:
            order = get_object_or_404(Order, order_id=order_id)
            print(f"Order filtered: {order}")
            
            order.payment_method = payment_method
            order.status = 'for-booking'
            order.save()
            return JsonResponse({'success': True})
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Order not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


    
    
class WarehouseDashboardView(TemplateView):
    template_name = 'admin/warehouse-dashboard.html'
    title = "Warehouse Dashboard"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
    

        context.update({
            'title': self.title,
            'orders': Order.objects.all(),
        })
        return context
    
class LogisticsDashboardView(TemplateView):
    template_name = 'logistics/logistics-dashboard.html'
    title = "Logistics Dashboard"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
    

        context.update({
            'title': self.title,
            'orders': Order.objects.all(),
        })
        return context
    
class LogisticsUserDatabaseView(TemplateView):
    template_name = 'logistics/logistics-dashboard.html'
    title = "Logistics User Database"
    
class LogisticsUserDatabaseView(TemplateView):
    template_name = 'logistics/logistics-user-database.html'
    title = "Logistics Dashboard"
    
class LogisticsBookingView(View):
    template_name = 'logistics/logistics-booking.html'
    title = "Logistics Dashboard"

    def get(self, request, *args, **kwargs):
        address = None
        fulfiller = self.request.GET.get('fulfiller')
        
        orders = Order.objects.filter(Q(status='for-booking') | Q(status='for-pickup'))
        
        if fulfiller:
            orders = orders.filter(courier__fulfiller=fulfiller)
        else:
            orders = Order.objects.filter(Q(status='for-booking') | Q(status='for-pickup'))
        
        for order in orders:
            order.cod_amount = order.total_amount - order.discount
            address = order.shipping_address
            order.save()
        
        context = {
            'title': self.title,
            'orders': orders,
            'address': address,
        }
        return render(request, self.template_name, context)
    
def courier_booking_view(request):
    if request.method == 'POST':
        courier_id = request.POST.get('courier_id')
        print(f'Courier ID: {courier_id}')
        try:
            if courier_id:
                courier = get_object_or_404(Courier, id=courier_id)
                order = Order.objects.filter(courier=courier).first()
                if order:
                    order.status = 'for-pickup'
                    order.save()
                    print(f'Order Status: {order.status}')
                else:
                    return JsonResponse({'error': 'Order not found for the given courier ID.'}, status=404)
                form = CourierBookingForm(request.POST, instance=courier)
            else:
                form = CourierBookingForm(request.POST)
            if form.is_valid():
                form.save()
                return JsonResponse({'message': 'Form submitted successfully!'})
            else:
                errors = form.errors.as_json()
                return JsonResponse({'errors': errors}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        # Handle GET request or render the form page
        form = CourierBookingForm()
        return render(request, 'your_template.html', {'form': form})
    
def reject_order_view(request):
    if request.method == 'POST':
        courier_id = request.POST.get('courier_id')
        new_status = request.POST.get('new_status')
        rebooking_notes = request.POST.get('rebooking_notes')
        new_shipping_fee = request.POST.get('new_shipping_fee')
        print(f'Booking Notes: {rebooking_notes}')
        
        if not (courier_id and new_status):
            return JsonResponse({'error': 'Invalid request.'}, status=400)
        
        try:
            order = Order.objects.get(courier__id=courier_id)
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found.'}, status=404)
        
        order.status = new_status
        order.save()
        
        if rebooking_notes:
            courier = Courier.objects.get(id=courier_id)
            courier.booking_notes = rebooking_notes
            courier.save()
            
        if new_shipping_fee:
            courier = Courier.objects.get(id=courier_id)
            courier.actual_shipping_fee = new_shipping_fee
            courier.save()
        
        
        return JsonResponse({'message': 'Order status updated successfully.'})
    
    return JsonResponse({'error': 'Invalid request method.'}, status=405)
    
class LogisticsPickupView(TemplateView):
    template_name = 'logistics/logistics-pickup.html'
    title = "Logistics Pickup"
    
    def get(self, request, *args, **kwargs):
        address = None
        orders = Order.objects.filter(Q(status='for-pickup') | Q(status='shipping'))
        
        for order in orders:
            address = order.shipping_address
            order.save()
        
        context = {
            'title': self.title,
            'orders': orders,
            'address': address,
            
        }
        return render(request, self.template_name, context)
    
def logistics_pickup_data(request):
    orders = Order.objects.filter(status='for-pickup')
    records_total = orders.count()
    draw = int(request.GET.get('draw', 1))
    order_data = []
    for index, order in enumerate(orders, start=1):
        address = order.shipping_address
        products = [f"{item.quantity}x {item.product.name}" for item in order.orderitem_set.all()]
        order_dict = {
            'index': index,
            'pickup_date': f'<span>{order.courier.pickup_date.strftime("%B %d, %Y")}</span>',
            'order_id': f'<span>{order.order_id}</span>',
            'receiver': f'<h6><u>{address.first_name} {address.last_name}</u></h6><p>Location: {address.province}</p>',
            'courier': f'<h6><b>{order.courier.courier.upper()}: { order.courier.tracking_number}</b></h6><span>Pouch Size: { order.courier.pouch_size.title()}</span>',
            'products': "<ul>" + "".join([f"<li>{product}</li>" for product in products]) + "</ul>",
            'action': f'<button class="btn theme-btn action-btn" onclick="pickupOrder(this)" data-courier-id="{order.courier.id}">PICKED UP</button>'
                f'<button class="btn btn-danger action-btn" onclick="rebookOrder(this)" data-courier-id="{order.courier.id}">REBOOK</button>'

        }
        order_data.append(order_dict)
        
        # Construct the JSON response
    response = {
        'draw': draw,
        'recordsTotal': records_total,
        'recordsFiltered': records_total,
        'data': order_data,
    }

    return JsonResponse(response, safe=False)


class LogisticsBPEncodingView(TemplateView):
    template_name = 'logistics/logistics-bp-encoding.html'
    title = "Logistics BP Encoding"
    
class LogisticsReturnView(TemplateView):
    template_name = 'logistics/logistics-return.html'
    title = "Logistics Return"
    
def logistics_return_data(request):
    orders = Order.objects.filter(status='rts')
    records_total = orders.count()
    draw = int(request.GET.get('draw', 1))
    order_data = []
    for index, order in enumerate(orders, start=1):
        address = order.shipping_address
        products = [f"{item.quantity}x {item.product.name}" for item in order.orderitem_set.all()]
        order_dict = {
            'index': index,
            'pickup_date': f'<span>{order.courier.pickup_date.strftime("%B %d, %Y")}</span>',
            'order_id': f'<span>{order.order_id}</span>',
            'receiver': f'<h6><u>{address.first_name} {address.last_name}</u></h6><p>Location: {address.city}</p>',
            'courier': f'<h6><b>{order.courier.courier.upper()}: { order.courier.tracking_number}</b></h6><span>Pouch Size: { order.courier.pouch_size.title()}</span>',
            'products': "<ul>" + "".join([f"<li>{product}</li>" for product in products]) + "</ul>",
            'action': f'<button class="btn badge badge-returned" onclick="returnedOrder(this)" data-courier-id="{order.courier.id}">RETURNED</button>'

        }
        order_data.append(order_dict)
        
        # Construct the JSON response
    response = {
        'draw': draw,
        'recordsTotal': records_total,
        'recordsFiltered': records_total,
        'data': order_data,
    }

    return JsonResponse(response, safe=False)
    
class LogisticsVWApprovalView(TemplateView):
    template_name = 'logistics/logistics-approval.html'
    title = "Logistics VW Approval"
    
class LogisticsReceivingView(TemplateView):
    template_name = 'logistics/logistics-receiving.html'
    title = "Logistics Receiving"
    
class LogisticsProductView(TemplateView):
    template_name = 'logistics/logistics-product.html'
    title = "Logistics Product"
    
def logistics_product_orders_data(request):
    filter_param = request.GET.get('filter')
    print(f'Filtered Status: {filter_param}')
    if filter_param:
        orders = Order.objects.filter(status=filter_param)
    else:
        orders = Order.objects.filter(
            Q(status='for-pickup') | Q(status='shipping') | Q(status='delivered') | 
            Q(status='paid') | Q(status='bp-encoded') | Q(status='vw-paid') | 
            Q(status='rts') | Q(status='returned')
        )
        
    print(f'Orders: {orders}')
    records_total = orders.count()
    draw = int(request.GET.get('draw', 1))


    order_data = []
    for index, order in enumerate(orders, start=1):
        address = order.shipping_address
        products = [f"[{item.quantity}x]  {item.product.name}" for item in order.orderitem_set.all()]
        seller = order.user.referred_by
        
        pickup_date = f'<span>{order.courier.pickup_date.strftime("%B %d, %Y")}</span>'
        order_id = f'<span>{order.order_id}</span>'
        receiver = f'<h6><u>{address.first_name} {address.last_name}</u></h6><p>Mobile: {address.phone}</p><p>Location: {address.city}</p><p style="margin-top:5px;"><b><i>**Seller Info</i></b></p><p>Seller Name: {seller.first_name} {seller.last_name}</p><p>Seller Mobile: {seller.mobile}</p>'
        courier = f'<h6><b>{order.courier.courier.upper()}: <a href="" style="color: #3255AD;">{order.courier.tracking_number}</a></b></h6><p>Amount: <b>₱ {order.cod_amount}</b></p><p>Pouch Size: {order.courier.pouch_size.title()}</p><p>Fulfiller: {order.courier.fulfiller}</p>'
        if order.courier.booking_notes:
            courier += f'<p style="margin-top: 10px">***Shipping Notes: {order.courier.booking_notes}</p>'
        products = "<ul>" + "".join([f"<li>{product}</li>" for product in products]) + "</ul>"
        
        if order.status == "for-pickup":
            status = f'<button class="btn badge badge-{order.status}" onclick="rebookOrder(this)" data-courier-id="{order.courier.id}" data-customer-name="{order.shipping_address.first_name}">FOR PICKUP</button>'
        elif order.status == "shipping":
            status = f'<button class="btn badge badge-{order.status}" onclick="shipOrder(this)" data-courier-id="{order.courier.id}" data-courier-tracking="{order.courier.tracking_number}">SHIPPING</button>'
        elif order.status == "delivered":
            status = f'<button class="btn badge badge-{order.status}" onclick="deliveredOrder(this)" data-courier-id="{order.courier.id}" data-courier-tracking="{order.courier.tracking_number}" data-courier-actual-sf="{order.courier.actual_shipping_fee}">DELIVERED</button>'
        else:
            status = f'<button class="btn badge badge-{order.status}">{order.status.upper().replace("-", " ")}</button>'
            
        order_dict = {
            'index': index,
            'pickup_date': pickup_date,
            'order_id': order_id,
            'receiver': receiver,
            'courier': courier,
            'products': products,
            'status': status,
        }
        order_data.append(order_dict)

    response = {
        'draw': draw,
        'recordsTotal': records_total,
        'recordsFiltered': records_total,
        'data': order_data,
    }

    return JsonResponse(response, safe=False)
    
class LogisticsPackageView(TemplateView):
    template_name = 'logistics/logistics-package.html'
    title = "Logistics package"
    
class LogisticsSanteBranchView(TemplateView):
    template_name = 'logistics/logistics-twc-sante-branch.html'
    title = "Logistics TWC Sante Branch"
    
class LogisticsPhysicalStocksView(TemplateView):
    template_name = 'logistics/logistics-physical-stocks.html'
    title = "Logistics Physical Stocks"
    
class DashboardLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        # Redirect to the specified URL after logout
        return redirect('https://www.twconline.store')


        


    

    
