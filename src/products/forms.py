from django import forms
from .models import Product
from django.forms import formset_factory

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'sku',
            'slug',
            'category_1',
            'category_2',
            'name',
            'description_1',
            'description_2',
            'feature',
            'advantage',
            'benefit',
            'specification',
            'image_1',
            'image_2',
            'image_3',
            'image_4',
            'image_5',
            'supplier_price',
            'franchisee_price',
            'distributor_price',
            'seller_price',
            'customer_price',
        ]