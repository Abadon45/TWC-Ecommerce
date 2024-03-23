from django.views.generic import FormView, TemplateView
from allauth.account.views import LoginView as AllauthLoginView
from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.views import PasswordResetCompleteView, PasswordChangeView
from allauth.account.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.encoding import force_bytes
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.db import transaction, IntegrityError
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect

from orders.models import Order
from user.models import UserManager

from user.forms import CustomUserCreationForm, CustomPasswordChangeForm

User = get_user_model()


class RegisterView(FormView):
    template_name = 'login/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('home_view')

    def form_valid(self, form):
        try:
            with transaction.atomic():
                user = form.save(commit=False)
                raw_password = form.cleaned_data.get('password1')
                user.set_password(raw_password)
                user.save()
                user.refresh_from_db()

                user = authenticate(username=user.username, password=raw_password)
                login(self.request, user)

        except IntegrityError as e:
            print(user.__dict__)
            raise e

        return super(RegisterView, self).form_valid(form)
    

class EcomLoginView(AllauthLoginView):
    redirect_authenticated_user = False
    template_name = 'login/login.html'

    def get_success_url(self):
        # Your custom success URL logic here
        return reverse_lazy('home_view')

    def form_invalid(self, form):
        # Your custom form invalid handling logic here
        return super().form_invalid(form)

# class EcomLoginView(BaseLoginView):
#     redirect_authenticated_user = False
#     template_name = 'login/login.html'
    
#     def get_success_url(self):
#         User = get_user_model()
#         user = User.objects.get(username=self.request.user.username)
#         session_key = self.request.session.session_key
        
#         if not session_key:
#             self.request.session.create()
#             session_key = self.request.session.session_key

#         anonymous_order = Order.objects.filter(session_key=session_key, complete=False).first()
        
#         if anonymous_order:
#             anonymous_order.save()
#             if 'guest_user' in self.request.session:
#                 del self.request.session['guest_user']
#             return reverse('cart:cart')
#         else:
#             self.request.session['guest_order'] = False

#         return reverse('home_view')

#     def form_invalid(self, form):
#         messages.error(self.request, 'Invalid username or password')
#         return self.render_to_response(self.get_context_data(form=form))

class ForgotPasswordView(SuccessMessageMixin, PasswordResetView):
    title = "Password Reset"
    template_name = 'login/password-reset.html'
    subject_template_name = 'login/password-reset-subject.html'
    success_message = "We've emailed you instructions for setting your password, " \
                    "if an account exists with the email you entered. You should receive them shortly." \
                    " If you don't receive an email, " \
                    "please make sure you've entered the address you registered with, and check your spam folder."
                    
    from_email= settings.EMAIL_MAIN
    success_url = reverse_lazy('home_view')
    
class PasswordResetComplete(PasswordResetCompleteView):
    template_name = "login/password-reset-complete.html"
    title = "Password Reset Complete"
    
class ChangePasswordView(PasswordChangeView):
    template_name = 'login/change-password.html'
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy('login:password_done')
    
class PasswordDoneView(TemplateView):
    template_name = 'login/change-password-done.html'
    
