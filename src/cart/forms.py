from django.forms import ModelForm
from django import forms
from .models import *


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


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            'first_name',
            'last_name',
            'phone',
            'region',
            'province',
            'city',
            'barangay',
            'line1',
            'line2',
            'postcode',
            'message',
        ]

