from django.views.generic import TemplateView, FormView
from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from billing.models import Customer
from orders.models import Order

from .forms import CustomUserCreationForm


class RegisterView(FormView):
    template_name = 'login/register.html'
    form_class = CustomUserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('home_view')

    def form_valid(self, form):
        print("Form is valid!")
        user = form.save()
        
        customer, created = Customer.get_or_create_customer(user=user, email=user.email)
        
        if user is not None:
            login(self.request, user)
        return super(RegisterView, self).form_valid(form)
    
    
class EcomLoginView(BaseLoginView):
    redirect_authenticated_user = False
    template_name = 'login/login.html'
    
    def get_success_url(self):
        # Check if the user is not authenticated and has an anonymous order
        if not self.request.user.is_authenticated:
            session_key = self.request.session.session_key
            
            if not session_key:
                # If session_key is not available, create a new session
                self.request.session.create()
                session_key = self.request.session.session_key

            anonymous_order = Order.objects.filter(session_key=session_key, complete=False).first()
            
            if anonymous_order:
                # Merge the anonymous order with the authenticated user's order
                if self.request.user.customer:
                    anonymous_order.customer = self.request.user.customer
                    anonymous_order.save()
                    del self.request.session['guest_user']
                    return reverse('cart:cart')

        # If no anonymous order or user is authenticated, redirect to home page
        return reverse('home_view')

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password')
        return self.render_to_response(self.get_context_data(form=form))

class ForgotPasswordView(TemplateView):
    title="Forgot Password"
    template_name = 'login/forgot-password.html'

