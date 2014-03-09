__author__ = 'Jarvis'

from django import forms
from offer import models as offerModels


class OfferForm(forms.ModelForm):
    class Meta:
        model = offerModels.Offer
        exclude = {'publisher'}