
from django.urls import path
from .views import ProductListView, ProductCreateView, ProductDetailView

app_name = 'products'
urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('add-product/', ProductCreateView.as_view(), name='add_product'),
    path('<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),



]