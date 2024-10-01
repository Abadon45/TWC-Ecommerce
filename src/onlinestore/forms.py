from django.forms import ModelForm
from django import forms
from .models import *


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

