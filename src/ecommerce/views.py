from django.views.generic import View, TemplateView
from django.shortcuts import render
from django.http import HttpResponseNotFound



class AboutUsView(TemplateView):
    title="About Us"
    template_name = 'about.html'

class IndexView(TemplateView):
    title="Home"
    template_name = 'index.html'

class ContactView(TemplateView):
    title="Contact"
    template_name = 'contact.html'

class ErrorView(TemplateView):
    title="404"
    template_name = '404.html'

class BecomeSellerView(TemplateView):
    title="BecomeSeller"
    template_name = 'become-seller.html'

class ComingSoonView(TemplateView):
    title="ComingSoon"
    template_name = 'coming-soon.html'

class FaqView(TemplateView):
    title="Faqs"
    template_name = 'faq.html'

class HelpView(TemplateView):
    title="Help"
    template_name = 'help.html'

class MailSuccessView(TemplateView):
    title="MailSuccess"
    template_name = 'mail-sucess.html'

class PrivacyView(TemplateView):
    title="Privacy"
    template_name = 'privacy.html'

class ReturnView(TemplateView):
    title="return"
    template_name = 'return.html'

class TeamView(TemplateView):
    title="Team"
    template_name = 'team.html'

class TermView(TemplateView):
    title="Terms"
    template_name = 'terms.html'

class TestimonialView(TemplateView):
    title="Testimonial"
    template_name = 'testimonial.html'

class Handle404View(View):
    def get(self, request, exception=None):
        return HttpResponseNotFound(render(request, '404.html'))



