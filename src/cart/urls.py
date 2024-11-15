from django.urls import path
from .views import *
from .utils import create_order
from django.conf import settings
from django.conf.urls.static import static

app_name = 'cart'
urlpatterns = [
    path('', CartView.as_view(), name='cart'),
    path('update-item/', UpdateCartView.as_view(), name='update_item'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('checkout/promo/', PromoCheckoutView.as_view(), name='promo_checkout'),
    path('submit-checkout/', submit_checkout, name='submit_checkout'),
    path('submit-promo-checkout/', submit_promo_checkout, name='submit_promo_checkout'),
    path('checkout/complete/', CheckoutDoneView.as_view(), name='checkout_complete'),
    path('checkout/create-order/', create_order, name='create_order'),
    path('checkout/promo/thank-you', PromoCheckoutDoneView.as_view(), name='promo_checkout_done'),
    path('xendit-webhook/', xendit_webhook, name='xendit_webhook'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)