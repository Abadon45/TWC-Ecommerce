from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'mobile', 'email', 'first_name', 'last_name', 'birth_date', 'date_activated', 'expiration_date', 'affiliate_code', 'is_seller', 'is_member', 'is_supplier', 'is_expired', 'is_active', 'is_staff', 'is_admin', 'timestamp', 'updated')
    
    readonly_fields = ('affiliate_code',)

admin.site.register(User, UserAdmin)