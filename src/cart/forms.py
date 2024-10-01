from django.forms import ModelForm
from .models import *

class CourierBookingForm(ModelForm):
    class Meta:
        model = Courier
        fields = ['fulfiller', 'courier', 'tracking_number', 'pouch_size', 'pickup_date', 'actual_shipping_fee', 'paid_by_fulfiller', 'booking_notes' ]

