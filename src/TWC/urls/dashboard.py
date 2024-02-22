# dashboard.py
from django.urls import path, include
from django.conf import settings
from django.views.generic import RedirectView
from user.views import get_order_details, DashboardView, SellerDashboardView
from TWC.urls import IndexView, BecomeSellerView
from django.contrib import admin
from user.views import RegisterGuestView

admin.autodiscover()

if settings.DEBUG:
    port = ':8000'
else:
    port = ''

app_name='dashboard'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('login/', include('login.urls')),
    path('cart/', include('cart.urls')),
    path('home/', IndexView.as_view(), name='home_view'),
    path('shop/', include('shop.urls')),
    path('become-seller/', BecomeSellerView.as_view(), name='become_seller'),
    path('products/', include('products.urls')),
    path('admin/', RedirectView.as_view(url=f'http://admin.{settings.SITE_DOMAIN}{port}/')),
    path('seller/', SellerDashboardView.as_view(), name='seller_dashboard'),
    path('get_order_details/', get_order_details, name='get_order_details'),
    path('shop/<int:referrer_id>/', RegisterGuestView.as_view(), name='register_guest'),
]