from django import forms
from .models import Product, Rating, Review
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
        
class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['score']
        widgets = {
            'score': forms.Select(choices=[(i, f'{i} Stars') for i in range(1, 6)], attrs={'class': 'form-control form-select'}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Your Review*'}),
        }