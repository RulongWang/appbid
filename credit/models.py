__author__ = 'rulongwang'

from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin

#credit change log + increase _reduce
class CreditPoint(models.Model):

    user = models.OneToOneField(User)
    credit_points = models.IntegerField(default=100)  # credit point


class CreditLog(models.Model):

    user = models.ForeignKey(User)
    credit_point = models.ForeignKey(CreditPoint)
    change_reason = models.TextField(null=True,blank=True)
