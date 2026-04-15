from django import forms
from accounts.models import User
from accounts.phone_validate import validate_phone_number
from datetime import date
from django.core.exceptions import ValidationError
import re

# Standard email regex
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# ----------------------------------
# RegisterForm
# ----------------------------------
class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'contact_number',
            'date_of_birth',
            'gender',
        ]

    # -------------------------
    # Email validation
    # -------------------------
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email is required.")

        # Format validation
        if not re.match(EMAIL_REGEX, email):
            raise forms.ValidationError("Invalid email format.")

        # Duplicate check (case-insensitive)
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email is already registered.")

        return email

    # -------------------------
    # First name validation
    # -------------------------
    def clean_first_name(self):
        name = self.cleaned_data.get("first_name")
        if not name or name.lower() == "hi" or name.isdigit():
            raise forms.ValidationError("Enter a valid first name.")
        return name

    # -------------------------
    # Last name validation
    # -------------------------
    def clean_last_name(self):
        name = self.cleaned_data.get("last_name")
        if not name or name.lower() == "hi" or name.isdigit():
            raise forms.ValidationError("Enter a valid last name.")
        return name

    # -------------------------
    # Date of birth validation
    # -------------------------
    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if age < 15:
                raise ValidationError("Minimum age is 15.")
        return dob

    # -------------------------
    # Phone number validation
    # -------------------------
    def clean_contact_number(self):
        phone = self.cleaned_data.get('contact_number')
        if phone and not validate_phone_number(phone):
            raise forms.ValidationError("Invalid phone number.")
        return phone

    # -------------------------
    # Password validation
    # -------------------------
    def clean_password2(self):
        password1 = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return password2

    # -------------------------
    # Save user
    # -------------------------
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data.get("password"))
        user.is_active = True  # optionally set to False if you want email activation
        if commit:
            user.save()
        return user
    
# ----------------------------
# LoginForm
# ----------------------------
class LoginForm(forms.Form):
    email = forms.EmailField(
        label='Email', 
        widget=forms.EmailInput(attrs={'placeholder': 'Email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )

  
# -----------------------------------
# User Update Form
# -----------------------------------
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'gender',
            'profile',
            'date_of_birth',
            'contact_number',
        ]
        
    # first_name validation
    def clean_first_name(self):
        name = self.cleaned_data.get("first_name")
        if name.lower() == "hi" or name.isdigit():
            raise forms.ValidationError("Please provide a valid first_name")
        return name
    
    # last_name validation
    def clean_last_name(self):
        name = self.cleaned_data.get("last_name")
        if name.lower() == "hi" or name.isdigit():
            raise forms.ValidationError("Please provide a valid last_name")
        return name
    
    # date_of_birth validation
    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if age < 15:
                raise ValidationError("Minimum age is 15.")
        return dob
    
    # phone validation
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not validate_phone_number(phone):
            raise forms.ValidationError(
                "Invalid phone number. Only BD, USA, Canada, UK formats allowed."
            )
        return phone
    
    
