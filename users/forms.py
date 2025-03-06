from django import forms
from django.contrib.admin.forms import AdminAuthenticationForm

class CustomAdminAuthenticationForm(AdminAuthenticationForm):
    username = forms.CharField(
        label="Username Or Email",  
        max_length=254,
        widget=forms.TextInput(attrs={'autofocus': True})
    )