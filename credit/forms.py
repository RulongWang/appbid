__author__ = 'Jarvis'

from django import forms
from credit import models


class AppraisementForm(forms.ModelForm):
    class Meta:
        model = models.Appraisement
        exclude = {'user', 'transaction'}