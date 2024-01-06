from django.forms import ModelForm
from .models import Order, OrderItem

class OrderForm(ModelForm):
    class Meta:
        model = Order
        exclude = ['user', 'address', 'payment_method', 'order_number']

class OrderItemForm(ModelForm):
    class Meta:
        model = OrderItem
        exclude = ['order']
