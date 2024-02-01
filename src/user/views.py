from django.views.generic import View, TemplateView
from django.shortcuts import render
from orders.models import Order
from addresses.models import Address
from user.utils import create_or_get_guest_user

class DashboardView(TemplateView):
    template_name = 'user/dashboard.html'
    title = "User Dashboard"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            customer = self.request.user.customer
            
        elif self.request.user.is_anonymous:
            customer = create_or_get_guest_user(self.request)
            
        context['customer'] = customer
        context = {
            'title': self.title,
            'customer': customer,
            'orders': Order.objects.filter(customer=customer),
            'addresses': Address.objects.filter(customer=customer),
        }
        
        return context
