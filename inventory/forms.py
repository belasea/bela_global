from django import forms
from django.forms import Textarea
from .models import Inventory


class DateInput(forms.DateInput):
    input_type = 'date'


class ProductInventoryCreateForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = [
            'pro_id',
            'purchase_date',
            'quantity_cost',
            'purchase_quantity',
            'stock_quantity',
            'seller',
            'quantity_updated',
            'expiry_date',
        ]

        # Override the Customer some fields
        widgets = {
            'seller': Textarea(attrs={'rows': 3, 'cols': 3}),
            'purchase_date': DateInput(attrs={'type': 'date'}),
            'expiry_date': DateInput(attrs={'type': 'date'})
        }