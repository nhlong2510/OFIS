from django import forms
from django.contrib.auth.models import User


class RegisterForm(forms.ModelForm):
    first_name = forms.CharField(label='First Name', widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "First Name",
    }))
    last_name = forms.CharField(label='Last Name', widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Last Name",
    }))
    username = forms.CharField(label='Username', widget=forms.TextInput(attrs={
        "class": "form-control", 
        "placeholder": "Username",
    }))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={
        "class": "form-control", 
        "placeholder": "Email",
    }))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={
        "class": "form-control", 
        "placeholder": "Password",
    }))
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={
        "class": "form-control", 
        "placeholder": "Confirm Password",
    }))
    is_active = forms.BooleanField(label='Activate')
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password', 'is_active']