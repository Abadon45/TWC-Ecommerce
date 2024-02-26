from django.contrib import admin
from django import forms
from .models import Product

# admin.site.register(Product)

class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'class': 'vLargeTextField'}),
        }

class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = [
            'sku',
            'slug',
            'category_1',
            'category_2',
            'name',
            'supplier_price',
            'franchisee_price',
            'distributor_price',
            'seller_price',
            'customer_price',
        ]

admin.site.register(Product, ProductAdmin)