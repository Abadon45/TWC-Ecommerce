# dashboard.py
from django.urls import path, include
from django.conf import settings
from django.views.generic import RedirectView
from user.views import DashboardView
from TWC.urls import IndexView, BecomeSellerView
from django.contrib import admin

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
    # path('admin-interface/', admin.site.urls),  # new line
]