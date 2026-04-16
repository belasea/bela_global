import re
from django import forms
from django.forms import Textarea
from .models import Contact, ReplayContact
from contacts.utils import validate_phone_number

# Standard email regex (basic)
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# General international phone number: optional +, 10–15 digits
PHONE_REGEX = r'^\+?\d{10,15}$'
NAME_REGEX = r"^[A-Za-z\s]+$"

# ContactForm ==============================================
class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone',
            'subject',
            'message',
        ]
        widgets = {
            'message': Textarea(attrs={'rows': 3, 'cols': 3}),
        }
    
    # First Name validation
    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        if not first_name:
            raise forms.ValidationError("First name is required")
        if not re.match(NAME_REGEX, first_name):
            raise forms.ValidationError("First name must contain only letters")
        if first_name.lower() == "hi":
            raise forms.ValidationError("Please provide a valid first name")
        return first_name


    # Last Name validation
    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name")
        if not last_name:
            raise forms.ValidationError("Last name is required")
        if not re.match(NAME_REGEX, last_name):
            raise forms.ValidationError("Last name must contain only letters")
        if last_name.lower() == "hi":
            raise forms.ValidationError("Please provide a valid last name")
        return last_name

    # Email validation
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not re.match(EMAIL_REGEX, email):
            raise forms.ValidationError("Invalid email format")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not validate_phone_number(phone):
            raise forms.ValidationError(
                "Invalid phone number. Only BD, USA, Canada, UK formats allowed."
            )
        return phone

    

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