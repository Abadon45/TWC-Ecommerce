from django.contrib import admin
from .models import Order, OrderItem, Courier, Voucher

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'id', 'discount', 'subtotal', 'cod_amount', 'user', 'complete')
    inlines = [OrderItemInline]
    exclude = ('ordered_items',)
    
class CourierAdmin(admin.ModelAdmin):
    list_display = ('tracking_number', 'courier', 'fulfiller', 'pouch_size', 'actual_shipping_fee', 'pickup_date', 'paid_by_fulfiller')

admin.site.register(Courier, CourierAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Voucher)
