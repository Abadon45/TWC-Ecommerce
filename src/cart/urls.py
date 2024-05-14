from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

app_name = 'cart'
urlpatterns = [
    path('', CartView.as_view(), name='cart'),
    path('update-item/', updateItem, name='update_item'),
    path('checkout/', checkout, name='checkout'),
    path('bundle-checkout/', BundleCheckoutView.as_view(), name='bundle_checkout'),
    path('get-selected-address/', get_selected_address, name='get_selected_address'),
    path('edit-address/', edit_checkout_address, name='edit_checkout_address'),
    path('get-checkout-address-details/', get_checkout_address_details, name='get_checkout_address_details'),
    path('submit-checkout/', submit_checkout, name='submit_checkout'),
    path('checkout/complete/', checkout_done_view, name='checkout_complete'),
    path('checkout/orderid-session/', set_order_id_session_variable, name='set_order_id_session_variable'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)