from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control border-0 shadow-sm', 'placeholder': 'Full Name*'}),
            'email': forms.EmailInput(attrs={'class': 'form-control border-0 shadow-sm', 'placeholder': 'Email Address*'}),
            'body': forms.Textarea(attrs={'class': 'form-control border-0 shadow-sm', 'placeholder': 'Comment*', 'style': 'height: 150px'}),
        }