from django.contrib import admin
from .models import *

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')

admin.site.register(Address)
admin.site.register(Test)
