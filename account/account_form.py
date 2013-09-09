__author__ = 'rulongwang'
from django import forms
from django.utils.translation import ugettext as _
from django.contrib.admin import ModelAdmin
from django.contrib.auth.models import User
import models


class RegisterForm(forms.Form):
    email = forms.EmailField(
        max_length=30,
        widget=forms.TextInput(attrs={'size': 30})
    )
    password = forms.CharField(
        max_length=30,
        widget=forms.PasswordInput(attrs={'size': 20}),
        help_text='The password length must be more than 6.'
    )
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'size': 20})
    )

    def clean_username(self):
        users = User.objects.filter(username__iexact=self.cleaned_data["username"])
        if not users:
            return self.cleaned_data["username"]
        error_msg = _('%(name)s has been used.') % {'name': self.cleaned_data["username"]}
        raise forms.ValidationError(error_msg)

    def clean_email(self):
        emails = User.objects.filter(email__iexact=self.cleaned_data["email"])
        if not emails:
            return self.cleaned_data["email"]
        error_msg = _('%(email)s has been used.') % {'email': self.cleaned_data["email"]}
        raise forms.ValidationError(error_msg)


class UserDetails(forms.ModelForm):

    class Meta:
        model = models.UserDetails


class PublicProfile(forms.ModelForm):
    class Meta:
        model = models.UserPublicProfile

class EmailItems(forms.ModelForm):
    class Meta:
        model = models.email_items
