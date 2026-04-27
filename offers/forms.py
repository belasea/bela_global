from django import forms
from .models import Coupon

class DateInput(forms.DateInput):
    input_type = 'date'


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'valid_from', 'valid_to', 'coupon_discount', 'active']
        widgets = {
            'valid_from': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'valid_to': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class CouponApplyForm(forms.Form):
    code = forms.CharField()