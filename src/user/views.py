from django.views.generic import View, TemplateView
from django.shortcuts import render
from orders.models import Order
from addresses.models import Address
from user.utils import get_or_create_customer
from django.shortcuts import redirect
from django.urls import reverse
from billing.models import Customer
from django.http import HttpResponseRedirect
from django.conf import settings

class DashboardView(TemplateView):
    template_name = 'user/dashboard.html'
    title = "User Dashboard"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            customer = self.request.user.customer
            
        elif self.request.user.is_anonymous:
            customer = get_or_create_customer(self.request)
            
        context['customer'] = customer
        context = {
            'title': self.title,
            'customer': customer,
            'orders': Order.objects.filter(customer=customer),
            'addresses': Address.objects.filter(customer=customer),
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
        
        customer = self.request.user.customer
        if not customer:
            customer = get_or_create_customer(self.request)
            
        affiliate_link = self.request.user.generate_affiliate_link()

        context.update({
            'title': self.title,
            'customer': customer,
            'orders': Order.objects.filter(customer=customer),
            'addresses': Address.objects.filter(customer=customer),
            'affiliate_link': affiliate_link,
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
    
