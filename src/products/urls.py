from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import *

app_name = 'products'
urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('add-product/', product_create_view, name='add_product'),
    path('<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)