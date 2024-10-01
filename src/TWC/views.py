from django.contrib.admin.sites import AdminSite
from django.views.generic import FormView
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.http import HttpResponse
from user.forms import EmailForm
from django.conf import settings

class TWCAdminSite(AdminSite):
    def login(self, request, extra_context=None):
        response = super().login(request, extra_context)
        if request.user.is_authenticated and request.user.is_staff:
            return redirect('/admin/')
        return response

admin_site = TWCAdminSite()

class EmailFormView(FormView):
    template_name = 'test/test-email.html'
    form_class = EmailForm
    success_url = reverse_lazy('home_view')

    def form_valid(self, form):
        recipient_email = form.cleaned_data.get('email')
        subject = form.cleaned_data.get('subject')
        message = form.cleaned_data.get('message')
        from_email = settings.EMAIL_MAIN

        try:
            send_mail(
                subject,
                message,
                from_email,
                [recipient_email],
                fail_silently=False,
            )
            return super().form_valid(form)
        except Exception as e:
            return HttpResponse(f'Error: {e}')