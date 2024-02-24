from django.views.generic import TemplateView, FormView
from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.db import transaction
from django.db import IntegrityError

from billing.models import Customer
from orders.models import Order
from user.utils import get_or_create_customer
from user.models import UserManager

from user.forms import CustomUserCreationForm

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

                # Save the user instance before creating the Customer
                user.refresh_from_db()

                user = authenticate(username=user.username, password=raw_password)
                login(self.request, user)

                customer, created = Customer.objects.get_or_create(user=user)
                # customer, created = Customer.get_or_create_customer(user, self.request)

        except IntegrityError as e:
            print(user.__dict__)
            raise e

        return super(RegisterView, self).form_valid(form)
    

class EcomLoginView(BaseLoginView):
    redirect_authenticated_user = False
    template_name = 'login/login.html'
    
    def get_success_url(self):
        User = get_user_model()
        user = User.objects.get(username=self.request.user.username)
        # customer, created = Customer.objects.get_or_create(user=user)
        session_key = self.request.session.session_key
        
        if not session_key:
            self.request.session.create()
            session_key = self.request.session.session_key

        anonymous_order = Order.objects.filter(session_key=session_key, complete=False).first()
        
        if anonymous_order:
            # anonymous_order.customer = customer
            anonymous_order.save()
            if 'guest_user' in self.request.session:
                del self.request.session['guest_user']
            return reverse('cart:cart')
        else:
            self.request.session['guest_order'] = False

        return reverse('home_view')

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password')
        return self.render_to_response(self.get_context_data(form=form))

class ForgotPasswordView(TemplateView):
    title="Forgot Password"
    template_name = 'login/forgot-password.html'

