import json

import requests
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, TemplateView
from django.contrib.auth.views import PasswordResetCompleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, JsonResponse, Http404
from django.conf import settings
from allauth.account.views import PasswordResetView
from django.shortcuts import render, redirect
from django_hosts import reverse
from dotenv import load_dotenv

load_dotenv()

from cart.utils import detect_region, get_main_domain, fetch_and_update_user_session, get_user_access_token
from onlinestore.api import fetch_user_orders, get_tokens
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

        token_response = get_tokens(username, password)

        if "error" in token_response:
            return render(request, self.template_name, {"error": token_response["error"]})

        try:
            api_response = response.json()
        except ValueError:
            return render(request, self.template_name, {"error": "Invalid response from server."})

        if response.status_code == 200 and "token" in api_response:
            token = token_response.get("refresh_token")

            request.session["user_token"] = api_response.get("token")
            request.session["refresh_token"] = token
            request.session["access_token"] = token_response.get("access_token")
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

            # ✅ Create response
            next_url = request.GET.get("next", f"http://dashboard.{get_main_domain(request)}/")
            response = HttpResponseRedirect(
                f"http://dashboard.{get_main_domain(request)}/token/?token={token}&username={username}&next={next_url}")

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


class ChangePasswordView(LoginRequiredMixin, View):
    template_name = "login/change-password.html"
    CHANGE_PASSWORD_API_URL = settings.CHANGE_PASSWORD_API_URL

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        """Handle password change request."""
        try:
            data = json.loads(request.body)  # ✅ Correctly parse JSON request
            old_password = data.get("old_password")
            new_password = data.get("new_password")
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)

        if not old_password or not new_password:
            return JsonResponse({"error": "Both old and new passwords are required."}, status=400)

        refresh_token = request.session.get("refresh_token")
        access_token = get_user_access_token(refresh_token)

        if not access_token:
            return JsonResponse({"error": "User is not authenticated. Please log in again."}, status=401)

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        payload = {"old_password": old_password, "new_password": new_password}

        try:
            response = requests.post(self.CHANGE_PASSWORD_API_URL, json=payload, headers=headers)

            if response.status_code == 200:
                return JsonResponse({"message": "Password changed successfully."}, status=200)

            if response.status_code == 401:  # 🔁 Token expired, try refreshing
                if access_token:
                    headers["Authorization"] = f"Bearer {access_token}"
                    response = requests.post(self.CHANGE_PASSWORD_API_URL, json=payload, headers=headers)
                    if response.status_code == 200:
                        return JsonResponse({"message": "Password changed successfully."}, status=200)

            try:
                response_data = response.json()
            except requests.exceptions.JSONDecodeError:
                return JsonResponse({"error": "Invalid response from API."}, status=500)

            return JsonResponse(response_data, status=response.status_code)

        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": f"Request failed: {str(e)}"}, status=500)



class SaveTokenView(View):
    def get(self, request):
        token = request.GET.get("token")
        username = request.GET.get("username")
        next_url = request.GET.get("next", f"http://dashboard.{get_main_domain(request)}/")

        if token:
            request.session["refresh_token"] = token
            request.session["username"] = username
            print(f"✅ Token saved in session: {token}")

        # Redirect to the next URL
        return HttpResponseRedirect(next_url)




class UserSessionMixin:
    """Mixin to provide user session data to the context."""

    def get_user_session_data(self):
        """Fetch user session data."""
        user = self.request.user
        username = self.request.session.get("username", "")
        if username:
            fetch_and_update_user_session(self.request, username)
        return {
            "username": user.username,
            "first_name": self.request.session.get("first_name", ""),
            "middle_name": self.request.session.get("middle_name", ""),
            "last_name": self.request.session.get("last_name", ""),
            "image": self.request.session.get("image", "img/user/default_profile.png"),
            "email": self.request.session.get("email", ""),
            "mobile": self.request.session.get("mobile", ""),
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

        excluded_statuses = ["transfer_vw"]  # Can expand this list later if needed

        filtered_orders = [order for order in orders if order["status"] not in excluded_statuses]

        if filtered_orders:
            print("Available keys in order:", filtered_orders[0].keys())

            # Sort orders by timestamp (fallback to purchase_date)
        sorted_orders = sorted(
            filtered_orders,
            key=lambda x: x.get("timestamp", x.get("purchase_date", "")),
            reverse=True
        )

        # Define statuses that should NOT be counted as "pending"
        non_pending_statuses = ["in_progress", "delivered", "undelivered", "paid", "vw-paid", "rejected", "rts", "returned"]

        # Separate orders into pending and completed
        pending_orders = [order for order in filtered_orders if order["status"] not in non_pending_statuses]
        completed_orders = [order for order in filtered_orders if order["status"] == "completed"]

        # Update context with orders and session data
        context.update({
            "orders": sorted_orders[:10],  # Full orders list
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
        """Return context data for rendering the profile page."""
        user_token = self.request.session.get("user_token")
        refresh_token = self.request.session.get("refresh_token")
        access_token = self.request.session.get("access_token")

        print(f'UserToken: {user_token}')
        print(f'RefreshToken: {refresh_token}')
        print(f'AccessToken: {access_token}')

        # Try to refresh token if access_token is missing or expired
        if not access_token:
            access_token = get_user_access_token(refresh_token)
            if access_token:
                self.request.session["access_token"] = access_token

        context = super().get_context_data(**kwargs)
        context.update(self.get_user_session_data())  # Mixin method
        context.update({
            "UPDATE_PROFILE_API_URL": settings.UPDATE_PROFILE_API_URL.format(
                username=self.request.session.get("username")),
            "UPDATE_IMAGE_API_URL": settings.UPDATE_PROFILE_API_URL.format(
                username=self.request.session.get("username")),
            "ACCESS_TOKEN": access_token,
        })
        return context

    @method_decorator(csrf_exempt)  # Allow AJAX PUT/PATCH requests
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def put(self, request, *args, **kwargs):
        """Handle AJAX profile updates via PUT request."""
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            username = request.session.get("username", "")
            if username:
                fetch_and_update_user_session(request, username)
                return JsonResponse({"message": "Profile updated successfully."})
            return JsonResponse({"error": "Username not found in session."}, status=400)

        return JsonResponse({"error": "Method Not Allowed"}, status=405)

    def patch(self, request, *args, **kwargs):
        """Forward profile image update to external API."""
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            if "image" not in request.FILES:
                return JsonResponse({"error": "No image uploaded."}, status=400)

            image_file = request.FILES["image"]
            username = request.session.get("username", "")
            access_token = request.session.get("access_token", "")

            if not username:
                return JsonResponse({"error": "Username not found in session."}, status=400)

            if not access_token:
                return JsonResponse({"error": "Unauthorized"}, status=401)

            # API URL
            api_url = settings.UPDATE_PROFILE_API_URL.format(username=username)

            # Prepare request data
            files = {"image": (image_file.name, image_file, image_file.content_type)}
            headers = {"Authorization": f"Bearer {access_token}"}

            # Send the request to the API
            response = requests.patch(api_url, files=files, headers=headers)

            # Forward the response back to the frontend
            if response.status_code == 200:
                return JsonResponse(response.json())
            else:
                return JsonResponse(response.json(), status=response.status_code)

        return JsonResponse({"error": "Method Not Allowed"}, status=405)


class DashboardOrderView(UserSessionMixin, TemplateView):
    template_name = "user/dashboard-order-history.html"
    excluded_statuses = ["transfer_vw"]

    status_map = {
        "for-pickup": ["afs", "for-pickup", "paid", "vw-paid"],  # To Ship
        "shipping": ["shipping"],  # To Receive
        "delivered": ["delivered"],  # Delivered
    }

    def get_filtered_orders(self, all_orders, status_filter):
        """Filters orders based on the selected status."""
        status_filter = status_filter.lower().strip()  # Normalize input
        print(f"🔍 Filtering with status: '{status_filter}'")  # Debugging

        if status_filter == "all":
            return all_orders  # Show all orders when 'all' is selected

        # Get expected statuses based on the filter (default to provided status if not mapped)
        expected_statuses = self.status_map.get(status_filter, [status_filter])

        print(f"✅ Expected statuses: {expected_statuses}")  # Debugging

        # Apply filtering
        filtered_orders = [order for order in all_orders if order["status"].lower() in expected_statuses]

        print(f"📌 Filtered Orders Count: {len(filtered_orders)}")
        for order in filtered_orders:
            print(f"🔹 Order {order['order_number']} | Status: {order['status']}")

        return filtered_orders

    def get_all_orders(self):
        """Fetch and return all orders excluding unwanted statuses."""
        user = self.request.user
        order_data = fetch_user_orders(user.username) if user.is_authenticated else {"orders": [], "count": 0}

        # Exclude unwanted statuses
        all_orders = [order for order in order_data["orders"] if order["status"] not in self.excluded_statuses]

        print(f"✅ Total Orders After Exclusion: {len(all_orders)}")
        return all_orders

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get all orders
        all_orders = self.get_all_orders()

        # Compute counts BEFORE filtering
        pending_count = sum(1 for order in all_orders if order["status"] == "pending")
        to_ship_count = sum(1 for order in all_orders if order["status"] in self.status_map["for-pickup"])
        shipping_count = sum(1 for order in all_orders if order["status"] in self.status_map["shipping"])
        delivered_count = sum(1 for order in all_orders if order["status"] in self.status_map["delivered"])

        # Apply filtering ONLY for displayed orders
        status_filter = self.request.GET.get("status", "all").strip().lower()
        print(f"🔎 Status Filter (Context Data): '{status_filter}'")  # Debugging
        filtered_orders = self.get_filtered_orders(all_orders, status_filter)

        print(f"📊 Final Orders Count for '{status_filter}': {len(filtered_orders)}")  # Debugging

        # Update context
        context.update({
            "orders": filtered_orders,
            "pending_count": pending_count,
            "to_ship_count": to_ship_count,
            "shipping_count": shipping_count,
            "delivered_count": delivered_count,
        })
        context.update(self.get_user_session_data())

        return context

    def get(self, request, *args, **kwargs):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            status_filter = request.GET.get("status", "all").strip().lower()
            print(f"🔎 Status Filter (AJAX GET): '{status_filter}'")

            # ✅ Fetch all orders again (AJAX request is separate from initial page load)
            all_orders = self.get_all_orders()

            # ✅ Apply filtering for AJAX reques
            filtered_orders = self.get_filtered_orders(all_orders, status_filter)

            print(f"📌 Filtered Orders Count (AJAX): {len(filtered_orders)}")
            for order in filtered_orders:
                print(f"🔹 Order {order.get('order_number', 'N/A')} | Status: {order['status']}")

            return JsonResponse({"orders": filtered_orders, "count": len(filtered_orders)})

        return super().get(request, *args, **kwargs)


class DashboardOrderDetailView(TemplateView, UserSessionMixin):
    def get_context_data(self, **kwargs):
        user = self.request.user
        order_number = kwargs.get("order_number")
        order_data = fetch_user_orders(user.username) if user.is_authenticated else {"orders": [], "count": 0}

        filtered_order = next((order for order in order_data["orders"] if order["order_number"] == order_number), None)

        if filtered_order:
            try:
                filtered_order["subtotal"] = float(filtered_order["cod_amount"]) - 120
            except (TypeError, ValueError):
                filtered_order["subtotal"] = 0

        region = filtered_order["address"]["region"]
        region_group = detect_region(region)
        courier = filtered_order["courier"]
        print(f'courier: {courier}')

        for_shipping = ['afs', 'for-pickup', 'shipping', 'pickup', 'delivered', 'paid', 'vw-paid']
        shipping = ["shipping", "delivered", "paid", "vw-paid"]
        delivered = ["delivered", "paid", "vw-paid"]

        context = super().get_context_data(**kwargs)
        context.update({
            "order": filtered_order,
            "region_group": region_group,
            "for_shipping": for_shipping,
            "shipping": shipping,
            "delivered": delivered,
        })
        context.update(self.get_user_session_data())
        return context

    def get(self, request, *args, **kwargs):
        """Ensure authentication and redirection logic is handled by UserSessionMixin."""
        return UserSessionMixin.get(self, request, *args, **kwargs)
