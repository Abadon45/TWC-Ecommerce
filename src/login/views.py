from django.views.generic import TemplateView, FormView
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from billing.models import Customer

from .forms import CustomUserCreationForm




class RegisterView(FormView):
    template_name = 'login/register.html'
    form_class = CustomUserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('home_view')

    def form_valid(self, form):
        print("Form is valid!")
        user = form.save()
        
        #create a Customer for new regitered users
        customer, created = Customer.get_or_create_customer(user=user, email=user.email)
        
        if user is not None:
            login(self.request, user)
        return super(RegisterView, self).form_valid(form)
    
    
class EcomLoginView(LoginView):
    redirect_authenticated_user = False
    template_name = 'login/login.html'
    
    def get_success_url(self):
        # Check if the request originated from the checkout page
        referer = self.request.META.get('HTTP_REFERER')
        if referer and 'checkout' in referer:
            return reverse('cart:checkout')
        else:
            return reverse('home_view')  # Replace with your desired redirect afte
    
    def form_invalid(self, form):
        messages.error(self.request,'Invalid username or password')
        return self.render_to_response(self.get_context_data(form=form))
    

class ForgotPasswordView(TemplateView):
    title="Forgot Password"
    template_name = 'login/forgot-password.html'

