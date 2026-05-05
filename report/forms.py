from django import forms
from django.forms import Textarea
from django.forms import ModelChoiceField
from .models import CustomerReport


class DateInput(forms.DateInput):
    input_type = 'date'


class CustomerReportForm(forms.ModelForm):

    class Meta:
        model = CustomerReport
        fields = [
            'order_conf_date',
            'country',
            'delivery_conformations',
            'notes',
            'customer_type',
            'parcel_send_receipt',
        ]

        # Override the Customer some fields
        widgets = {
            'order_conf_date': DateInput(attrs={'type': 'date'}),
            'country': forms.Select(attrs={
                'class': 'form-select',
                'disabled': 'disabled'  # This locks the field
            }),
            'notes': Textarea(attrs={'rows': 1, 'cols': 1}),
        }


class CustomerReportAddForm(forms.ModelForm):

    class Meta:
        model = CustomerReport
        fields = [
            'order',
        ]