__author__ = 'rulongwang'

from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin



class CreditPoint(models.Model):
    """credit change log + increase _reduce"""
    user = models.OneToOneField(User)
    points = models.IntegerField(default=100)

    def __unicode__(self):
        return ' '.join([self.user.username, ':', str(self.points)])


class CreditLog(models.Model):
    user = models.ForeignKey(User)
    credit_point = models.ForeignKey(CreditPoint)
    change_reason = models.TextField(null=True,blank=True)
    points = models.IntegerField()
    create_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return ' '.join([self.user.username, ':', str(self.points), self.change_reason, str(self.create_time)])

admin.site.register(CreditPoint)
admin.site.register(CreditLog)
