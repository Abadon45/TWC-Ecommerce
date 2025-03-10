import requests
from django.contrib import messages
from django.utils.functional import SimpleLazyObject
from django.views.generic import View, TemplateView, FormView
from django.contrib.auth.views import PasswordResetCompleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.db.models import Q
from django.core.paginator import Paginator
from decimal import Decimal
from django.contrib.humanize.templatetags.humanize import intcomma
from allauth.account.views import LoginView as AllauthLoginView
from allauth.account.views import PasswordResetView
from django.db import transaction, IntegrityError
from django.shortcuts import render, redirect
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.utils import detect_region, get_main_domain
from onlinestore.api import fetch_user_orders
from user.forms import LoginForm

import logging

from .auth_backends import APIAuthenticationBackend
from .utils import fulfiller

logger = logging.getLogger(__name__)
User = get_user_model()


AUTH_API_URL = settings.AUTH_API_URL


class APILoginView(View):
    template_name = "login/login.html"
    title = "Login"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Authenticate via external API
        api_url = settings.AUTH_API_URL  # Ensure this is correctly set in settings.py
        response = requests.post(api_url, json={"username": username, "password": password})  # Use JSON, not form data

        try:
            api_response = response.json()
        except ValueError:
            return render(request, self.template_name, {"error": "Invalid response from server."})

        if response.status_code == 200 and "token" in api_response:
            request.session["access_token"] = api_response["token"]
            request.session["username"] = api_response["user"]
            request.session["is_authenticated"] = True
            request.session["sponsor"] = api_response.get("sponsor", None)  # Store sponsor from API response
            request.session["expires_at"] = api_response["expires"]  # Store token expiry time
            request.session["first_name"] = api_response.get("first_name", "")  # Store first name
            request.session["middle_name"] = api_response.get("middle_name", "")  # Store middle name
            request.session["last_name"] = api_response.get("last_name", "")  # Store last name
            request.session["image"] = api_response.get("image", None)  # Store image URL
            request.session["is_seller"] = api_response.get("is_seller", False)  # Store seller status
            request.session["is_member"] = api_response.get("is_member", False)  # Store member status

            # Set session expiration (1 day)
            request.session.set_expiry(60 * 60 * 24)

            print(f"Login successful! Token stored for {username}")
            print(f'Sponsor: {api_response.get("sponsor")}')
            print(f'User details: {api_response.get("first_name")} {api_response.get("last_name")}, Seller: {api_response.get("is_seller")}')

            # Redirect to dashboard
            main_domain = get_main_domain(request)
            return redirect(f"http://dashboard.{main_domain}")

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


class UserSessionMixin:
    """Mixin to provide user session data to the context."""

    def get_user_session_data(self):
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

class DashboardProfileView(TemplateView, UserSessionMixin):
    template_name = "user/dashboard-profile.html"
    title = "User Profile"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Add session-based user data
        context.update(self.get_user_session_data())

        # Fetch additional user fields
        context.update({
            "username": user.username,
        })

        return context



class DashboardOrderView(TemplateView, UserSessionMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({})
        context.update(self.get_user_session_data())
        return context


class DashboardOrderDetailView(TemplateView, UserSessionMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({})
        context.update(self.get_user_session_data())
        return context
