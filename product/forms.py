# forms.py
from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'title', 'slug', 'featured', 'price', 'thumbnail', 'description', 'in_stock']
