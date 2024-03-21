from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'customer', 'user', 'complete')
    inlines = [OrderItemInline]
    exclude = ('ordered_items',)

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
