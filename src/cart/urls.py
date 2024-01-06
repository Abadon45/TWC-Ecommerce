from django.urls import path
from .views import *

app_name = 'cart'
urlpatterns = [
    path('', TemplateView.as_view(template_name='cart/shop-cart.html'), name='cart'),
    path('update-item/', updateItem, name='update_item'),
    # path('update-item/<int:product_id>/<str:action>/', updateItem, name='update_item'),
    path('checkout/', checkout, name='checkout'),
    path('checkout/complete/', checkout_done_view, name='checkout_complete'),
]
