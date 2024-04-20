# dashboard.py
from django.urls import path, include
from django.conf import settings
from django.views.generic import RedirectView
from user.views import *
from TWC.urls import IndexView, BecomeSellerView
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
    path('', IndexView.as_view(), name='home_view'),
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
    path('logistics/member', LogisticsUserDatabaseView.as_view(), name='member'),
    path('logistics/bp-encoding/', LogisticsBPEncodingView.as_view(), name='bp_encoding'),
    path('logistics/package/', LogisticsPackageView.as_view(), name='package'),
    path('logistics/physical-stocks/', LogisticsPhysicalStocksView.as_view(), name='physical_stocks'),
    path('logistics/pickup/', LogisticsPickupView.as_view(), name='pickup'),
    path('logistics/pickup/pickup-data', logistics_pickup_data, name='pickup_data'),
    path('logistics/product/', LogisticsProductView.as_view(), name='product'),
    path('logistics/product/logistics-product-orders-data', logistics_product_orders_data, name='products_data'),
    path('logistics/receiving/', LogisticsReceivingView.as_view(), name='receiving'),
    path('logistics/return/', LogisticsReturnView.as_view(), name='return'),
    path('logistics/return/return-data', logistics_return_data, name='return_data'),
    path('logistics/twc-sante-branch/', LogisticsSanteBranchView.as_view(), name='twc_sante_branch'),
    path('logistics/approval/', LogisticsVWApprovalView.as_view(), name='approval'),
    path('logistics/booking/', logistics_booking_data, name='booking_data'),
    path('logistics/booking/courier-booking-view', courier_booking_view, name='courier_booking_view'),
    path('logistics/booking/reject-order-view', reject_order_view, name='reject_order'),
    path('profile/', dashboard_redirect),
    path('address/', dashboard_redirect),
    path('track-order/', dashboard_redirect),
    path('delete-address/', delete_address, name='delete_address'),
    path('update-address/', update_address, name='update_address'),
    path('get-address-details/', get_address_details, name='get_address_details'),
    path('get_order_details/', get_order_details, name='get_order_details'),
    path('shop/<int:referrer_id>/', RegisterGuestView.as_view(), name='register_guest'),
    path('logout/', DashboardLogoutView.as_view(), name='logout'),
    
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)