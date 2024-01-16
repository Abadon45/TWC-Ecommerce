from django.views.generic import View, TemplateView
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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "HOME"
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
