from django import forms
from .models import Address

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['first_name', 'last_name', 'email', 'phone', 'line1', 'line2', 'city', 'postcode', 'message']
