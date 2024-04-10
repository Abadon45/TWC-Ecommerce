# dashboard.py
from django.urls import path, include
from django.conf import settings
from django.views.generic import RedirectView
from user.views import *
from TWC.urls import IndexView, BecomeSellerView
from django.views.generic import TemplateView
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
    path('login/', include('login.urls')),
    path('cart/', include('cart.urls')),
    path('home/', IndexView.as_view(), name='home_view'),
    path('shop/', include('shop.urls')),
    path('become-seller/', BecomeSellerView.as_view(), name='become_seller'),
    path('products/', include('products.urls')),
    path('admin/', RedirectView.as_view(url=f'http://admin.{settings.SITE_DOMAIN}{port}/'), name='admin'),
    path('seller/', SellerDashboardView.as_view(), name='seller_dashboard'),
    path('seller/review-order/<str:order_id>/', ReviewOrderView.as_view(), name='review_order'),
    path('seller/update-discount/', update_discount, name='update_discount'),
    path('seller/confirm_order/', confirm_order, name='confirm_order'),
    path('warehouse/', WarehouseDashboardView.as_view(), name='warehouse'),
    path('logistics/', LogisticsDashboardView.as_view(), name='logistics'),
    path('profile/', dashboard_redirect),
    path('address/', dashboard_redirect),
    path('track-order/', dashboard_redirect),
    path('delete-address/', delete_address, name='delete_address'),
    path('update-address/', update_address, name='update_address'),
    path('get-address-details/', get_address_details, name='get_address_details'),
    path('get_order_details/', get_order_details, name='get_order_details'),
    path('shop/<int:referrer_id>/', RegisterGuestView.as_view(), name='register_guest'),
    
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)