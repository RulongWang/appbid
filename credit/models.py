__author__ = 'rulongwang'

from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin



class CreditPoint(models.Model):
    """credit change log + increase _reduce"""
    user = models.OneToOneField(User)
    points = models.IntegerField(default=100)


class CreditLog(models.Model):
    user = models.ForeignKey(User)
    credit_point = models.ForeignKey(CreditPoint)
    change_reason = models.TextField(null=True,blank=True)
    points = models.IntegerField()
    create_time = models.DateTimeField(auto_now_add=True)


admin.site.register(CreditPoint)
admin.site.register(CreditLog)
