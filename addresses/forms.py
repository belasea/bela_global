import re
from django import forms
from accounts.models import User
from .models import Address
from addresses.phone_validate import validate_phone_number

EMAIL_REGEX = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"



class BillingForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'country', 'contact_number']


class shippingForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            'first_name',
            'last_name',
            'email',
            'contact_number',
            'address',
            'city',
            'location',
            'country',
        ]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and not re.match(EMAIL_REGEX, email):
            raise forms.ValidationError('Invalid email format')
        if email == '.edu':
            raise forms.ValidationError(".edu email not allowed")
        return email

    def clean_city(self):
        city = self.cleaned_data.get("city")
        if not city.isalpha():
            raise forms.ValidationError("City must contain only letters")
        return city
    
    def clean_location(self):
        location = self.cleaned_data.get("location")
        if not location.isalpha():
            raise forms.ValidationError("location must contain only letters")
        return location
    
    def clean_address(self):
        address = self.cleaned_data.get("address")
        if not address.isalpha():
            raise forms.ValidationError("Address must contain only letters")
        return address
    
    # phone validation
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not validate_phone_number(phone):
            raise forms.ValidationError(
                "Invalid phone number. Only BD, USA, Canada, UK formats allowed."
            )
        return phone
    

"""
    <div class="pro-card p-4 mb-4 bg-white border shadow-sm">
                                        <h5 class="pro-section-label mb-4">Billing Address (Profile)</h5>
                                        <div class="row">
                                            <div class="col-md-6 mb-3">
                                                <label class="small text-muted">Account Email</label>
                                                <input name="email" class="form-control pro-input" 
                                                    value="{{ billing_form.email.value|default:'' }}" required>
                                            </div>
                                            <div class="col-md-6 mb-3">
                                                <label class="small text-muted">Default Country</label>
                                                <select class="form-select pro-input" name="country">
                                                    {% for value, name in billing_form.fields.country.choices %}
                                                        <option value="{{ value }}" {% if billing_form.country.value == value %}selected{% endif %}>
                                                            {{ name }}
                                                        </option>
                                                    {% endfor %}
                                                </select>
                                            </div>
                                        </div>
                                    </div>   
"""