from django import forms
from . import common_resources as resource
import re


class SignUpForm(forms.Form):
    org_email = forms.CharField(widget=forms.TextInput(attrs={"name":"org_email","placeholder":"Email"}),required=True)
    org_alias = forms.CharField(widget=forms.TextInput(attrs={"name":"org_alias","placeholder":"Organization alias","style":"text-transform:uppercase"}),required=True, min_length=2,max_length=4)
    password = forms.CharField(widget=forms.TextInput(attrs={"name":"password","placeholder":"Password - at least 6 chars","type":"password"}),required=True)
    re_password = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Repeat your password","type":"password"}),required=True)
    def clean(self):
        cleaned_data = super().clean()
        org_email = cleaned_data.get('org_email')
        org_alias = cleaned_data.get('org_alias')
        password = cleaned_data.get('password')
        re_password = cleaned_data.get('re_password')
        if not re.fullmatch(resource.email_regex,org_email):
            raise forms.ValidationError('Please enter a valid email address')
        if len(org_alias)<2:
            raise forms.ValidationError('Alias will be at least 2 characters long')
        if len(password)<6:
            raise forms.ValidationError('Enter a password of at least 6 characters')
        if password!=re_password:
            raise forms.ValidationError("Passwords don't match")
class SignInForm(forms.Form):
    org_email = forms.CharField(widget=forms.TextInput(attrs={"name":"org_email","placeholder":"Email"}),required=True)
    password = forms.CharField(widget=forms.TextInput(attrs={"name":"password","placeholder":"Password - at least 6 chars","type":"password"}),required=True)
    def clean(self):
        cleaned_data = super().clean()
        org_email = cleaned_data.get('org_email')
        password = cleaned_data.get('password')
        if not re.fullmatch(resource.email_regex,org_email):
            raise forms.ValidationError('Please enter a valid email address')
        if len(password)<6:
            raise forms.ValidationError('You\'re trying a short password')