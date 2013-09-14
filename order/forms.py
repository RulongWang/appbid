__author__ = 'Jarvis'

from django import forms
from order import models


class ServiceItemForm(forms.ModelForm):
    class Meta:
        model = models.ServiceItem