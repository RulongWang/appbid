__author__ = 'jarvis'
from django import forms
from appbid import models


class AppForm(forms.ModelForm):
    class Meta:
        model = models.App
        exclude = {'publisher', 'status'}

