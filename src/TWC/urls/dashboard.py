# dashboard.py
from django.urls import path, include
from django.conf import settings
from django.views.generic import RedirectView
from user.views import *
from TWC.urls import IndexView
from django.contrib import admin
from user.views import RegisterGuestView
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy


admin.autodiscover()

if settings.DEBUG:
    port = ':8000'
else:
    port = ''

app_name='dashboard'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('profile/', DashboardProfileView.as_view(), name='dashboard_profile'),
    path('address/', DashboardAddressView.as_view(), name='dashboard_address'),
    path('address/add-address', DashboardAddAddressView.as_view(), name='dashboard_add_address'),
    path('order-history/', DashboardOrderHistoryView.as_view(), name='dashboard_order'),
    path('load-more-orders/', load_more_orders, name='load_more_orders'),
    path('order/', DashboardOrderListView.as_view(), name='dashboard_order_list'),
    path('order/order-detail/', DashboardOrderDetailView.as_view(), name='dashboard_order_detail'),
    path('login/', include('login.urls')),
    path('cart/', include('cart.urls')),
    path('', IndexView.as_view(), name='home_view'),
    path('shop/', include('shop.urls')),
    path('products/', include('products.urls')),
    path('admin/', RedirectView.as_view(url=f'http://admin.{settings.SITE_DOMAIN}{port}/'), name='admin'),


    path('get-address-details/', get_address_details, name='get_address_details'),
    path('shop/<int:referrer_id>/', RegisterGuestView.as_view(), name='register_guest'),
    path('logout/', DashboardLogoutView.as_view(), name='logout'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)