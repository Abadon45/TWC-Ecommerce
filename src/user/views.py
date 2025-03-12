import requests
from django.views.generic import View, TemplateView
from django.contrib.auth.views import PasswordResetCompleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, JsonResponse
from django.conf import settings
from allauth.account.views import PasswordResetView
from django.shortcuts import render, redirect
from dotenv import load_dotenv

load_dotenv()

from cart.utils import detect_region, get_main_domain
from onlinestore.api import fetch_user_orders
from user.forms import LoginForm

import logging

from .auth_backends import APIAuthenticationBackend
from .utils import fulfiller

logger = logging.getLogger(__name__)
User = get_user_model()


AUTH_API_URL = settings.AUTH_API_URL


from django.shortcuts import redirect, render
import requests
from django.conf import settings
from django.http import HttpResponseRedirect

class APILoginView(View):
    template_name = "login/login.html"
    title = "Login"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Authenticate via external API
        api_url = settings.AUTH_API_URL
        response = requests.post(api_url, json={"username": username, "password": password})

        try:
            api_response = response.json()
        except ValueError:
            return render(request, self.template_name, {"error": "Invalid response from server."})

        if response.status_code == 200 and "token" in api_response:
            token = api_response["token"]

            request.session["access_token"] = token
            request.session["username"] = api_response["user"]
            request.session["is_authenticated"] = True
            request.session["sponsor"] = api_response.get("sponsor", None)
            request.session["expires_at"] = api_response["expires"]
            request.session["first_name"] = api_response.get("first_name", "")
            request.session["middle_name"] = api_response.get("middle_name", "")
            request.session["last_name"] = api_response.get("last_name", "")
            request.session["image"] = api_response.get("image", None)
            request.session["is_seller"] = api_response.get("is_seller", False)
            request.session["is_member"] = api_response.get("is_member", False)

            # Set session expiration (1 day)
            request.session.set_expiry(60 * 60 * 24)

            print(f"Login successful! Token stored for {username}")
            print(f"Token is {token}")
            print(f'Sponsor: {api_response.get("sponsor")}')
            print(f'User details: {api_response.get("first_name")} {api_response.get("last_name")}, Seller: {api_response.get("is_seller")}')

            # ✅ Create response
            response = HttpResponseRedirect(f"http://dashboard.{get_main_domain(request)}/token/?token={token}&username={username}")
            return response

        return render(request, self.template_name, {"error": "Invalid credentials"})


class LogoutView(View):
    def get(self, request):
        subdomain = request.session.get("sponsor")
        main_domain = get_main_domain(request)

        # Construct the redirect URL
        redirect_url = f"http://{subdomain}.{main_domain}" if subdomain else f"http://{main_domain}"

        request.session.flush()
        return redirect(redirect_url)


class ForgotPasswordView(SuccessMessageMixin, PasswordResetView):
    title = "Password Reset"
    template_name = 'login/password-reset.html'
    subject_template_name = 'login/password-reset-subject.html'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."

    from_email = settings.EMAIL_MAIN
    success_url = reverse_lazy('home_view')


class PasswordResetComplete(PasswordResetCompleteView):
    template_name = "login/password-reset-complete.html"
    title = "Password Reset Complete"


class PasswordDoneView(TemplateView):
    template_name = 'login/change-password-done.html'


class SaveTokenView(View):
    def get(self, request):
        token = request.GET.get("token")
        username = request.GET.get("username")

        if token:
            # Save token in session
            request.session["access_token"] = token
            request.session["username"] = username
            print(f"✅ Token saved in session: {token}")

        # Redirect to dashboard
        return HttpResponseRedirect(f"http://dashboard.{get_main_domain(request)}/")


class UserSessionMixin:
    """Mixin to provide user session data to the context."""

    def get_user_session_data(self):
        """Fetch user session data."""
        user = self.request.user
        return {
            "username": user.username,
            "first_name": self.request.session.get("first_name", ""),
            "middle_name": self.request.session.get("middle_name", ""),
            "last_name": self.request.session.get("last_name", ""),
            "image": self.request.session.get("image", "img/user/default_profile.png"),
            "email": self.request.session.get("email", ""),
            "mobile": self.request.session.get("sponsor_mobile", ""),
            "messenger_link": self.request.session.get("messenger_link", ""),
        }

    def get(self, request, *args, **kwargs):
        """Redirect unauthenticated users and return the view."""
        main_domain = get_main_domain(request)
        host = request.get_host()
        subdomain = host.split('.')[0]  # Extract subdomain

        redirect_url = f"http://{subdomain}.{main_domain}" if subdomain else f"http://{main_domain}"

        if subdomain != "dashboard":
            return redirect(redirect_url)  # Redirect to login/home

        context = self.get_context_data(**kwargs)  # Get default context
        context.update(self.get_user_session_data())  # Merge user session data

        return render(request, self.template_name, context)


class DashboardView(TemplateView, UserSessionMixin):
    template_name = "user/dashboard.html"
    title = "Dashboard Home"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Fetch user orders safely
        order_data = fetch_user_orders(user.username) if user.is_authenticated else {"orders": [], "count": 0}
        orders = order_data.get("orders", [])

        # Define statuses that should NOT be counted as "pending"
        non_pending_statuses = ["in_progress", "delivered", "undelivered", "paid", "vw-paid", "rejected", "rts", "returned"]

        # Separate orders into pending and completed
        pending_orders = [order for order in orders if order["status"] not in non_pending_statuses]
        completed_orders = [order for order in orders if order["status"] == "completed"]

        # Update context with orders and session data
        context.update({
            "orders": orders,  # Full orders list
            "pending_order_count": len(pending_orders),
            "completed_order_count": len(completed_orders),
        })

        # Add session data from mixin
        context.update(self.get_user_session_data())

        return context


class DashboardProfileView(View, UserSessionMixin):
    template_name = "user/dashboard-profile.html"
    title = "User Profile"

    def dispatch(self, request, *args, **kwargs):
        """Redirect unauthenticated users and allow PUT requests."""
        if request.method.upper() == "PUT":
            return self.put(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Helper method to generate context data."""
        context = self.get_user_session_data()
        context.update({
            "UPDATE_PROFILE_API_URL": settings.UPDATE_PROFILE_API_URL.format(username=self.request.user.username),
            "REFRESH_TOKEN": self.request.session.get("access_token"),
        })
        return context

    def get(self, request, *args, **kwargs):
        """Ensure authentication and redirect logic is handled by UserSessionMixin."""
        return super().get(request, *args, **kwargs)  # Calls UserSessionMixin's `get()`

    def put(self, request, *args, **kwargs):
        """Handle profile update via AJAX (PUT request)."""
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"message": "Profile updated successfully."})

        return JsonResponse({"error": "Method Not Allowed"}, status=405)



class DashboardOrderView(UserSessionMixin, TemplateView):
    def get_context_data(self, **kwargs):
        """Generate context data including user session details."""
        context = super().get_context_data(**kwargs)
        context.update(self.get_user_session_data())
        return context

    def get(self, request, *args, **kwargs):
        """Ensure authentication and redirection logic is handled by UserSessionMixin."""
        return UserSessionMixin.get(self, request, *args, **kwargs)  # Explicitly call UserSessionMixin's `get()`


class DashboardOrderDetailView(TemplateView, UserSessionMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({})
        context.update(self.get_user_session_data())
        return context

    def get(self, request, *args, **kwargs):
        """Ensure authentication and redirection logic is handled by UserSessionMixin."""
        return UserSessionMixin.get(self, request, *args, **kwargs)
