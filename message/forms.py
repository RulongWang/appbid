__author__ = 'Jarvis'

from django import forms
from message import models


class MessageForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'id': 'message_subject'}))
    class Meta:
        model = models.Message
