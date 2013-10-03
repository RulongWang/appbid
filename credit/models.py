__author__ = 'rulongwang'

from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin


class CreditCoin(models.Model):

    user = models.OneToOneField(User)
    credit_points = models.IntegerField(default=100)  # credit point
