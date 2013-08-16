__author__ = 'jarvis'
from django import forms
from appbid import models


class AppForm(forms.ModelForm):
    class Meta:
        model = models.App
        exclude = {'publisher'}


class AttachmentForm(forms.ModelForm):
    path = forms.FileField(
        label='Select a file'
    )
    class Meta:
        model = models.Attachment
        exclude = {'app'}