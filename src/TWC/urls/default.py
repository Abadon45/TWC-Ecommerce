from django.http import HttpRequest
from django.urls import path, include
from django.shortcuts import redirect
from onlinestore.views import *
from user.views import *


def conditional_home_view(request: HttpRequest):
    """Serves DashboardView if the subdomain is 'dashboard', otherwise IndexView."""
    host = request.get_host()
    subdomain = host.split('.')[0]  # Extract subdomain

    if subdomain == "dashboard":
        return DashboardView.as_view()(request)  # Serve DashboardView directly
    return IndexView.as_view()(request)  # Serve IndexView directly


urlpatterns = [
    # Conditional Home View
    path('', conditional_home_view, name="home_redirect"),

    # Global pages
    path('mail-success/', TemplateView.as_view(template_name='mail-success.html'), name="mail_success"),
    path('terms/', TemplateView.as_view(template_name='terms.html'), name="terms"),
    path(
        'return-policy/',
        TemplateView.as_view(
            template_name='return-policy.html',
            extra_context={'title': 'TWC Store | Return Policy'}
        ),
        name="return_policy"
    ),
    path(
        'terms-of-service/',
        TemplateView.as_view(
            template_name='terms-of-service.html',
            extra_context={'title': 'TWC Store | Terms of Service'}
        ),
        name="terms_of_service"
    ),

    # Dashboard & Authentication
    path("login/", APILoginView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('change-password/', ChangePasswordView.as_view(template_name='login/change-password.html'), name='change-password'),
    path("token/", SaveTokenView.as_view(), name="user_token"),
    path('profile/', DashboardProfileView.as_view(template_name="user/dashboard-profile.html"), name='dashboard-profile'),
    path('order-history/', DashboardOrderView.as_view(template_name="user/dashboard-order-history.html"), name='order-history'),
    path('order-history/<str:order_number>', DashboardOrderDetailView.as_view(template_name="user/dashboard-order-detail.html"), name='order-detail'),

    # Store-related URLs
    path('shop/', include('TWC.urls.shop', namespace='shop')),
    path('cart/', include('cart.urls', namespace='cart')),
    path('accounts/', include('allauth.urls')),
    path('pf/', ProductFunnelView.as_view(), name='product_funnel'),
    path('pf-vw/<str:product>/', ProductFunnelView.as_view(), name='product_funnel_vw'),
    path('pf-ds/<str:product>/', ProductFunnelView.as_view(), name='product_funnel_ds'),
    path('pf/create-order', create_order, name='create_order'),
]

handler404 = Handle404View.as_view()
