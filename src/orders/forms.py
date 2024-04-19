from django.forms import ModelForm
from .models import Order, OrderItem, Courier


class OrderForm(ModelForm):
    class Meta:
        model = Order
        exclude = ['user', 'address', 'payment_method', 'order_number']

class OrderItemForm(ModelForm):
    class Meta:
        model = OrderItem
        exclude = ['order']

class CourierBookingForm(ModelForm):
    class Meta:
        model = Courier
        fields = ['fulfiller', 'courier', 'tracking_number', 'pouch_size', 'pickup_date', 'actual_shipping_fee', 'paid_by_fulfiller', 'booking_notes' ]
