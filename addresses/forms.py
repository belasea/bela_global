import re
from django import forms
from .models import Address
EMAIL_REGEX = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"


class AddressForm(forms.ModelForm):
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
    
    def clean_country(self):
        city = self.cleaned_data.get("country")
        if not city.isalpha():
            raise forms.ValidationError("City must contain only letters")
        return city