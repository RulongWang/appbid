__author__ = 'jarvis'

from django import forms
from appbid import models as appModels


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
        model = appModels.App
        exclude = {'publisher'}

    def __init__(self, *args, **kwargs):
        super(AppForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['apple_id'].widget.attrs['readonly'] = True
            self.fields['platform_version'].widget.attrs['readonly'] = True
            self.fields['rating'].widget.attrs['readonly'] = True
            self.fields['category'].widget.attrs['disabled'] = True
            self.fields['device'].widget.attrs['disabled'] = True


class AttachmentForm(forms.ModelForm):
    path = forms.FileField(
        label='Select a file'
    )

    class Meta:
        model = appModels.Attachment
        exclude = {'app'}


class AppInfoForm(forms.ModelForm):
    class Meta:
        model = appModels.AppInfo
        exclude = {'app'}

    def __init__(self, *args, **kwargs):
        super(AppInfoForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['price'].widget.attrs['readonly'] = True
