__author__ = 'rulongwang'
from django import forms
from django.contrib.admin import ModelAdmin
from django.contrib.auth.models import User
import models


class RegisterForm(forms.Form):
    email = forms.EmailField(max_length=30, widget=forms.TextInput(attrs={'size': 30}))
    password = forms.CharField(max_length=30, widget=forms.PasswordInput(attrs={'size': 20}))
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'size': 20}))

    def clean_username(self):
        users = User.objects.filter(username__iexact=self.cleaned_data["username"])
        if not users:
            return self.cleaned_data["username"]
        raise forms.ValidationError(''.join([self.cleaned_data["username"], " has been used."]))

    def clean_email(self):
        emails = User.objects.filter(email__iexact=self.cleaned_data["email"])
        if not emails:
            return self.cleaned_data["email"]
        raise forms.ValidationError(''.join([self.cleaned_data["email"], " has been used."]))


class UserDetails(forms.ModelForm):

    class Meta:
        model = models.UserDetails


class PublicProfile(forms.ModelForm):
    class Meta:
        model = models.UserPublicProfile

class EmailItems(forms.ModelForm):
    class Meta:
        model = models.email_items
