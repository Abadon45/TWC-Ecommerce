from django.views.generic import View, TemplateView
from django.http import JsonResponse, Http404
from django.shortcuts import render
from django.http import HttpResponseNotFound
from products.models import Product
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from user.models import Referral
from django.shortcuts import redirect
from django.utils.text import capfirst
from django.urls import reverse
from django.http import HttpResponseRedirect

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
    
    def get(self, request, username=None, *args, **kwargs):
        referrer = None
        if username:
            referrer = get_object_or_404(User, username=username)
            print(f"Referrer: {referrer.username}")
            
            request.session['referrer'] = referrer.username
            
            print(f"Referrer: {request.session['referrer']}")
            
            return HttpResponseRedirect(reverse('home_view'))
                
        guest_user_info = request.session.get('guest_user_data', {})
        new_guest_user = request.session.get('new_guest_user', False)
        
        products = Product.objects.filter(active=True)
        products_list = list(products)
        random_products = random.sample(products_list, min(len(products_list), 4)) if products_list else []
        rand_on_sale_products = random.sample(products_list, min(len(products_list), 3)) if products_list else []
        rand_best_seller_products = random.sample(products_list, min(len(products_list), 3)) if products_list else []
        rand_top_rated_products = random.sample(products_list, min(len(products_list), 3)) if products_list else []
        
        
        subcategories_choices = [
            ('health_wellness', 'Health and Wellness'),
            ('healthy_beverages', 'Healthy Beverages'),
            ('intimate_care', 'Intimate Care'),
            ('bath_body', 'Bath & Body'),
            ('watches', 'Watches'),
            ('bags', 'Bags'),
            ('accessories', 'Accessories'),
            # ('home_living', 'Home & Living'),
        ]
        
        subcategories = [category[0] for category in subcategories_choices]
        filtered_products = products.filter(category_2__in=subcategories)
        subcategory_counts = {subcategory: filtered_products.filter(category_2=subcategory).count() for subcategory in subcategories}
        subcategory_counts_display = {
            subcategory: {
                'name': capfirst(next((name for value, name in subcategories_choices if value == subcategory), 'Unknown')),
                'count': count
            } for subcategory, count in subcategory_counts.items()
        }
            
            
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
            'referrer': referrer if username else None,
            'categories': subcategory_counts_display,
            'is_authenticated': self.request.user.is_authenticated,
        }

        if new_guest_user:
            del request.session['new_guest_user']
            
        if request.is_ajax():
            return JsonResponse({
            'has_existing_order': request.session.get('has_existing_order', False),
            'email': guest_user_info.get('email'),
        })

        return render(request, self.template_name, context)
    
class ProductFunnelView(TemplateView):
    title = "Product Funnel"
    context = {'title': title}

    def get_template_names(self):
        product = self.kwargs.get('product', None)
        if product == 'barleyforcancer':
            return ['funnels/products/barley/cancer.html']
        elif product == 'barleyfordiabetes':
            return ['funnels/products/barley/diabetes.html']
        elif product == 'barleyforhighblood':
            return ['funnels/products/barley/high-blood.html']
        elif product == 'old-age':
            return ['funnels/products/fusion-coffee/old-age.html']
        elif product == 'weight-loss':
            return ['funnels/products/fusion-coffee/weight-loss.html']
        elif product == 'boost-coffee':
            return ['funnels/products/boost_coffee/index.html']
        else:
            return ['404.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.kwargs.get('username')
        product = self.kwargs.get('product')
        context.update({'username': username, 'product': product})
        return context
    
    
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
