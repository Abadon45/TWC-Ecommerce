from django.views.generic import View, TemplateView
from django.http import JsonResponse
from django.shortcuts import render
from django.http import HttpResponseNotFound
from products.models import Product
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from user.models import Referral
from billing.models import Customer
from django.shortcuts import redirect

import random


User = get_user_model()

class AboutUsView(TemplateView):
    title="About Us"
    template_name = 'about.html'
    context = {'title': title}
    
    def get_context_data(self, **kwargs):
        return self.context

class IndexView(TemplateView):
    template_name = 'index.html'
    
    def get(self, request, username=None, affiliate_code=None, *args, **kwargs):
        referrer = None
        if username and affiliate_code:
            referrer = get_object_or_404(User, username=username, affiliate_code=affiliate_code)
            if request.user.is_authenticated and hasattr(request.user, 'is_superuser') and not request.user.is_superuser:
                referred = request.user  # The user who accessed the page
                Referral.objects.create(referrer=referrer, referred=referred)
                print(f"User {referred.username} was successfully referred by {referrer.username}.")

        if referrer:
            # Create a Customer object for the referred user
            customer, created = Customer.get_or_create_customer(request.user, request, referrer_code=referrer.id)
            if created:
                print(f"Customer {customer.email} was successfully created for user {request.user.username}.")
            return redirect('home_view')
            
        
            
        guest_user_info = request.session.get('guest_user_data', {})
        new_guest_user = request.session.get('new_guest_user', False)
        
        products = list(Product.objects.filter(active=True))
        random_products = random.sample(products, min(len(products), 4)) if products else []
        rand_on_sale_products = random.sample(products, min(len(products), 3)) if products else []
        rand_best_seller_products = random.sample(products, min(len(products), 3)) if products else []
        rand_top_rated_products = random.sample(products, min(len(products), 3)) if products else []
        
        context = {
            'title': "HOME",
            'username': guest_user_info.get('username'),
            'password': guest_user_info.get('password'),
            'email': guest_user_info.get('email'),
            'new_guest_user': new_guest_user,
            'has_existing_order': request.session.get('has_existing_order', False),
            'products': products,
            'random_products': random_products,
            'rand_on_sale_products': rand_on_sale_products,
            'rand_best_seller_products': rand_best_seller_products,
            'rand_top_rated_products': rand_top_rated_products,
            'referrer': referrer if username and affiliate_code else None,
        }

        if new_guest_user:
            # Clear the flag so the notification is not shown again
            del request.session['new_guest_user']
            
        if request.is_ajax():
            return JsonResponse({
            'has_existing_order': request.session.get('has_existing_order', False),
            'email': guest_user_info.get('email'),
        })

        return render(request, self.template_name, context)
    
    
class ContactView(TemplateView):
    title="Contact"
    template_name = 'contact.html'
    context = {'title': title}
    
    def get_context_data(self, **kwargs):
        return self.context

class BecomeSellerView(TemplateView):
    title="BecomeSeller"
    template_name = 'become-seller.html'
    context = {'title': title}

    def get_context_data(self, **kwargs):
        return self.context

class ComingSoonView(TemplateView):
    title="ComingSoon"
    template_name = 'coming-soon.html'
    context = {'title': title}
    
    def get_context_data(self, **kwargs):
        return self.context

class FaqView(TemplateView):
    title="Faqs"
    template_name = 'faq.html'
    context = {'title': title}
    
    def get_context_data(self, **kwargs):
        return self.context

class HelpView(TemplateView):
    title="Help"
    template_name = 'help.html'
    context = {'title': title}
    
    def get_context_data(self, **kwargs):
        return self.context


class PrivacyView(TemplateView):
    title="Privacy"
    template_name = 'privacy.html'
    context = {'title': title}
    
    def get_context_data(self, **kwargs):
        return self.context


class TeamView(TemplateView):
    title="Team"
    template_name = 'team.html'
    context = {'title': title}
    
    def get_context_data(self, **kwargs):
        return self.context

class Handle404View(View):
    title="404"
    
    def get(self, request, exception=None):
        context = self.get_context_data()
        return HttpResponseNotFound(render(request, '404.html', context=context))
    
    def get_context_data(self, **kwargs): 
        return {'title': self.title}
