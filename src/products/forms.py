from django import forms
from .models import Product, ProductImage

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['id','name', 'category', 'brand', 'sku', 'price', 'discount_price', 'stock', 'stock_unit', 'description']

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image']

ProductImageFormSet = forms.inlineformset_factory(Product, ProductImage, form=ProductImageForm, extra=1, can_delete=True)
