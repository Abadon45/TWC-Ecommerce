from django.contrib import admin
from .models import Address

# class AddressAdmin(admin.ModelAdmin):
#     list_display = ['user', 'first_name', 'last_name', 'email', 'phone', 'line1', 'line2', 'city', 'postcode', 'message']
#     search_fields = ['user__username', 'first_name', 'last_name', 'email', 'phone', 'city', 'postcode']

admin.site.register(Address)