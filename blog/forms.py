from django import forms
from .models import Comment
from contacts.utils import validate_phone_number

import re
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
PHONE_REGEX = r'^\+?\d{10,15}$'
NAME_REGEX = r"^[A-Za-z\s]+$"

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control border-0 shadow-sm', 'placeholder': 'Full Name*'}),
            'email': forms.EmailInput(attrs={'class': 'form-control border-0 shadow-sm', 'placeholder': 'Email Address*'}),
            'body': forms.Textarea(attrs={'class': 'form-control border-0 shadow-sm', 'placeholder': 'Comment*', 'style': 'height: 150px'}),
        }


    # Name validation
    def clean_name(self):
        name = self.cleaned_data.get("name")
        if not name:
            raise forms.ValidationError("Name is required")
        if not re.match(NAME_REGEX, name):
            raise forms.ValidationError("Name must contain only letters")
        if name.lower() == "hi":
            raise forms.ValidationError("Please provide a valid Name")
        return name


    # Email validation
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not re.match(EMAIL_REGEX, email):
            raise forms.ValidationError("Invalid email format")
        return email

