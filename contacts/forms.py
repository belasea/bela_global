import re
from django import forms
from django.forms import Textarea
from .models import Contact, ReplayContact
from contacts.utils import validate_phone_number

# Standard email regex (basic)
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# General international phone number: optional +, 10–15 digits
PHONE_REGEX = r'^\+?\d{10,15}$'

# ContactForm ==============================================
class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = [
            'first_name',
            'last_name',
            'email',
            'subject',
            'message',
        ]
        widgets = {
            'message': Textarea(attrs={'rows': 3, 'cols': 3}),
        }
    
    # Name validation
    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        if first_name.lower() == "hi" or first_name.isdigit():
            raise forms.ValidationError("Please provide a valid name")
        return first_name

    # Email validation
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not re.match(EMAIL_REGEX, email):
            raise forms.ValidationError("Invalid email format")
        return email

    # def clean_phone(self):
    #     phone = self.cleaned_data.get('phone')
    #     if phone and not validate_phone_number(phone):
    #         raise forms.ValidationError(
    #             "Invalid phone number. Only BD, USA, Canada, UK formats allowed."
    #         )
    #     return phone

    

 # ReplayContactForm ======================
class ReplayContactForm(forms.ModelForm):
    class Meta:
        model = ReplayContact
        fields = [
            'replay',
            'message',
        ]
        # Override the Customer some fields
        widgets = {
            'message': Textarea(attrs={'rows': 4, 'cols': 4 }),
        }