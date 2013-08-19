__author__ = 'jarvis'
from django import forms
from appbid import models


class AppForm(forms.ModelForm):
    app_store_link = forms.URLField(
        required=False,
        help_text="Your app link in app store."
    )
    source_code = forms.BooleanField(
        required=False,
        help_text='Whether you provide the source code and document,when transferring the app.'
    )
    web_site = forms.URLField(
        required=False,
        help_text='The support web site link for your app.'
    )

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