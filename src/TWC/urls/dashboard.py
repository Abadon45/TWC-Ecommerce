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
    path('seller/seller-orders-data', seller_orders_data, name='seller_orders_data'),
    path('seller/review-order/<str:order_id>/', ReviewOrderView.as_view(), name='review_order'),
    path('seller/update-discount/', update_discount, name='update_discount'),
    path('seller/confirm_order/', confirm_order, name='confirm_order'),
    path('seller/member/sellers', SellerMemberSellersView.as_view(), name='member_sellers'),
    path('seller/member/distributor', SellerMemberDistributorView.as_view(), name='member_distributor'),
    path('seller/member/builders', SellerMemberBuildersView.as_view(), name='member_builders'),
    path('seller/member/leaders', SellerMemberLeadersView.as_view(), name='member_leaders'),
    path('seller/member/expired', SellerMemberExpiredView.as_view(), name='member_expired'),
    path('seller/pending/orders', SellerPendingOrdersView.as_view(), name='seller_pending_orders'),
    path('seller/pending/virtual-warehouse', SellerPendingVirtualWarehouseView.as_view(), name='pending_virtual_warehouse'),
    path('seller/pending/virtual-warehouse/vw-data', pending_vw_data, name='pending_vw_data'),
    path('seller/pending/ecash', SellerPendingEcashView.as_view(), name='pending_ecash'),
    path('seller/pending/ecash/ecash-data', pending_ecash_data, name='pending_ecash_data'),
    path('seller/pending/greenium', SellerPendingGreeniumView.as_view(), name='pending_greenium'),
    path('seller/pending/greenium/greenium-data', pending_greenium_data, name='pending_greenium_data'),
    path('seller/pending/membership', SellerPendingMembershipView.as_view(), name='pending_membership'),
    path('seller/pending/membership/membership-data', pending_membership_data, name='pending_membership_data'),
    path('seller/pending/onboarding', SellerPendingOnboardingView.as_view(), name='pending_onboarding'),
    path('seller/pending/onboarding/onboarding-data', pending_onboarding_data, name='pending_onboarding_data'),
    path('seller/virtual-warehouse/inventory', SellerVWInventoryView.as_view(), name='vw_inventory'),
    path('seller/virtual-warehouse/sales', SellerVWSalesView.as_view(), name='vw_sales'),
    path('seller/orders/dropshipping', SellerOrdersDropshippingView.as_view(), name='orders_dropshipping'),
    path('seller/orders/dropshipping/orders-dropshipping-data', orders_dropshipping_data, name='orders_dropshipping_data'),
    path('seller/orders/membership-package', SellerOrdersMembershipPackageView.as_view(), name='orders_membership_package'),
    path('seller/ecash', SellerEcashView.as_view(), name='ecash'),
    path('seller/ecash/ecash-data', ecash_data, name='ecash_data'),
    path('seller/topup-greenium', SellerTopupGreeniumView.as_view(), name='topup_greenium'),
    path('seller/topup-greenium/topup-data', topup_greenium_data, name='topup_greenium_data'),
    path('seller/subscription', SellerSubscriptionCodesView.as_view(), name='subscription'),
    path('seller/subscription.subscription-codes-data', subscription_codes_data, name='subscription_codes_data'),
    path('seller/rewards/twc', SellerRewardsTWCView.as_view(), name='rewards_twc'),
    path('logistics/', LogisticsDashboardView.as_view(), name='logistics'),
    path('logistics/member', LogisticsUserDatabaseView.as_view(), name='member'),
    path('logistics/bp-encoding/', LogisticsBPEncodingView.as_view(), name='bp_encoding'),
    path('logistics/bp-encoding/for-bp-encoding-data', for_bp_encoding_data, name='for_bp_encoding_data'),
    path('logistics/package/', LogisticsPackageView.as_view(), name='package'),
    path('logistics/package/package-data', logistics_package_data, name='logistics_package_data'),
    path('logistics/physical-stocks/', LogisticsPhysicalStocksView.as_view(), name='physical_stocks'),
    path('logistics/pickup/', LogisticsPickupView.as_view(), name='pickup'),
    path('logistics/pickup/pickup-data', logistics_pickup_data, name='pickup_data'),
    path('logistics/product/', LogisticsProductView.as_view(), name='product'),
    path('logistics/product/logistics-product-orders-data', logistics_product_orders_data, name='products_data'),
    path('logistics/return/', LogisticsReturnView.as_view(), name='return'),
    path('logistics/return/return-data', logistics_return_data, name='return_data'),
    path('logistics/approval/', LogisticsVWApprovalView.as_view(), name='approval'),
    path('logistics/approval/vw-approval-data', vw_approval_data, name='vw_approval_data'),
    path('logistics/receiving/', LogisticsReceivingView.as_view(), name='receiving'),
    path('logistics/approval/stocks-to-receive-data', stocks_to_receive_data, name='stocks_to_receive_data'),
    path('logistics/token-redemption', LogisticsTokenRedemptionView.as_view(), name='token_redemption'),
    path('logistics/approval/token-redemption-data', token_redemption_data, name='token_redemption_data'),
    path('logistics/twc-sante-branch/', LogisticsSanteBranchView.as_view(), name='twc_sante_branch'),
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