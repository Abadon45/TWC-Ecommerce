from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import *

app_name = 'products'
urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('add-product/', ProductCreateView.as_view(), name='add_product'),
    path('<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('rate-product/<int:product_id>/', RateProductView.as_view(), name='rate_product'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)