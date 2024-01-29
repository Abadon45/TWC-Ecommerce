from django.views.generic import View, TemplateView
from django.http import JsonResponse
from django.shortcuts import render
from django.http import HttpResponseNotFound



class AboutUsView(TemplateView):
    title="About Us"
    template_name = 'about.html'
    context = {'title': title}
    
    def get_context_data(self, **kwargs):
        return self.context

class IndexView(TemplateView):
    template_name = 'index.html'
    
    def get(self, request, *args, **kwargs):
        guest_user_info = request.session.get('guest_user_data', {})
        new_guest_user = request.session.get('new_guest_user', False)
        
        context = {
            'title': "HOME",
            'username': guest_user_info.get('username'),
            'password': guest_user_info.get('password'),
            'email': guest_user_info.get('email'),
            'new_guest_user': new_guest_user,
            'has_existing_order': request.session.get('has_existing_order', False),
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
