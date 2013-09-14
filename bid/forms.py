__author__ = 'Jarvis'

from django import forms
from bid import models


class BiddingForm(forms.ModelForm):
    class Meta:
        model = models.Bidding
        exclude = {'app', 'buyer'}

