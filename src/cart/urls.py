from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

app_name = 'cart'
urlpatterns = [
    path('', CartView.as_view(), name='cart'),
    path('update-item/', updateItem, name='update_item'),
    path('checkout/', checkout, name='checkout'),
    path('checkout/complete/', checkout_done_view, name='checkout_complete'),
    
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)