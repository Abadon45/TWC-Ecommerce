from django.views.generic import View, TemplateView
from django.shortcuts import render
from orders.models import Order
from addresses.models import Address

class DashboardView(TemplateView):
    template_name = 'user/dashboard.html'
    title = "dashboard"
    context = {'title': title}

    def get_context_data(self, **kwargs):
        customer = self.request.user.customer
        
        self.context['orders'] = Order.objects.filter(customer=customer)
        self.context['addresses'] = Address.objects.filter(customer=customer)
        
        return self.context
