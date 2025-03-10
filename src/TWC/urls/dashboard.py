# dashboard.py

from django.urls import path, include
from django.views.generic import RedirectView
from user.views import *
from TWC.urls import IndexView
from django.contrib import admin
from django.conf.urls.static import static

admin.autodiscover()

if settings.DEBUG:
    port = ':8000'
else:
    port = ''

app_name = 'dashboard'

urlpatterns = [
    #DASHBOARD URL
    path('', DashboardView.as_view(), name='dashboard'),
    path("token/", SaveTokenView.as_view(), name="user_token"),
    path('profile/', DashboardProfileView.as_view(template_name="user/dashboard-profile.html"), name='dashboard-profile'),
    path('order-history/', DashboardOrderView.as_view(template_name="user/dashboard-order-history.html"), name='order-history'),
    path('order-history/<str:order_number>', DashboardOrderDetailView.as_view(template_name="user/dashboard-order-detail.html"), name='order-detail'),

    path('login/', include('user.urls.login')),
    path('cart/', include('cart.urls')),
    # path('', IndexView.as_view(), name='home_view'),
    path('shop/', include('TWC.urls.shop')),
    path('admin/', RedirectView.as_view(url=f'http://admin.{settings.SITE_DOMAIN}{port}/'), name='admin'),

    # Other URL
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
]
