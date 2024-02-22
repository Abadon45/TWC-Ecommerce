from django.views.generic import View, TemplateView
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

import logging

User = get_user_model()

@cache_page(60 * 15)
def get_order_details(request):
    logger = logging.getLogger(__name__) 
    if request.method == 'GET':
        order_id = request.GET.get('order_id')
        if order_id:
            try:
                order = Order.objects.get(order_id=order_id)
                data = {
                    'order_id': order.order_id,
                    'created_at': order.created_at.strftime("%Y-%m-%d"),
                    'total_amount': order.total_amount,
                    'total_quantity': order.total_quantity,
                    'status': order.status,
                    'order_items': [
                        {
                            'product_name': item.product.name,
                            'quantity': item.quantity,
                            'price': item.get_total,
                        } for item in order.orderitem_set.all() 
                    ]
                }
                return JsonResponse(data)
            except Order.DoesNotExist:
                logger.exception("Order not found for order_id %s", order_id)
                return HttpResponseNotFound("Order not found")
            except Exception as e:
                logger.exception("Error getting order details for order_id %s", order_id)
                return HttpResponseBadRequest("Error getting order details")
        else:
            return HttpResponseBadRequest("Order ID is required")
    else:
        return HttpResponseBadRequest("Only GET method is allowed")


class DashboardView(TemplateView):
    template_name = 'user/dashboard.html'
    title = "User Dashboard"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            customer, created = Customer.get_or_create_customer(self.request.user, self.request)
            order = Order.objects.filter(customer=customer)
                     
        context['customer'] = customer
        context = {
            'title': self.title,
            'customer': customer,
            'orders': order,
            'addresses': Address.objects.filter(customer=customer),
            'ordered_items': OrderItem.objects.filter(order=order)
        }
        
        return context
 
    
class SellerDashboardView(TemplateView):
    template_name = 'seller/seller-dashboard.html'
    title = "Seller Dashboard"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_seller:
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
    

class RegisterGuestView(View):
    def get(self, request, *args, **kwargs):
        # Store the referrer_id in the session
        request.session['referrer_id'] = kwargs['referrer_id']
        # Mark the session as modified to make sure it gets saved
        request.session.modified = True
        # Redirect to the dashboard
        return HttpResponseRedirect(f'http://{settings.SITE_DOMAIN}/')
    
