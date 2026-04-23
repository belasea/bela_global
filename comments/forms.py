from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control custom-input', 'placeholder': 'e.g. Jayed Hossain'}),
            'email': forms.EmailInput(attrs={'class': 'form-control custom-input', 'placeholder': 'e.g. jayed@example.com'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': '4', 'placeholder': 'Share your experience...'}),
        }