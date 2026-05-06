from django import forms
from .models import WarehouseOrderDetail
from orders.models import Order

class DateInput(forms.DateInput):
    input_type = 'date'

class WarehouseOrderDetailForm(forms.ModelForm):
    order_number = forms.ModelChoiceField(queryset=Order.objects.all(), to_field_name="id", empty_label="Select Order")

    class Meta:
        model = WarehouseOrderDetail
        fields = ['order_number', 'date', 'request_by']
        widgets = {
            'date': DateInput(attrs={'type': 'date'})
        }

    def clean_order_number(self):
        order_number = self.cleaned_data.get('order_number')

        # Exclude the current instance when checking for duplicates
        if WarehouseOrderDetail.objects.filter(order_number=order_number).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(f'This order ID {order_number} is already in use.')

        return order_number