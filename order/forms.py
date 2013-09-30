__author__ = 'Jarvis'

from django import forms
from order import models


class ServiceItemForm(forms.ModelForm):
    class Meta:
        model = models.ServiceItem


class ServiceDetailForm(forms.ModelForm):
    class Meta:
        model = models.ServiceDetail
        exclude = {'app', 'serviceitem'}

    def __init__(self, *args, **kwargs):
        super(ServiceDetailForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['sn'].widget.attrs['disabled'] = True