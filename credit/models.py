__author__ = 'rulongwang'

from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from transaction import models as txnModels


class CreditPoint(models.Model):
    """credit change log + increase _reduce"""
    user = models.OneToOneField(User)
    points = models.IntegerField(default=100)

    def __unicode__(self):
        return ' '.join([self.user.username, ':', str(self.points)])


class CreditLog(models.Model):
    type = (
        (1, 'transaction'),
        (2, 'buy-credit'),#TODO:use it later.
    )
    user = models.ForeignKey(User)
    credit_point = models.ForeignKey(CreditPoint)
    change_reason = models.TextField(null=True, blank=True)
    points = models.IntegerField()
    type = models.IntegerField(null=True, choices=type)
    ref_id = models.IntegerField(null=True)
    create_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return ' '.join([self.user.username, ':', str(self.points), self.change_reason, str(self.create_time)])


class Appraisement(models.Model):
    user = models.ForeignKey(User)
    transaction = models.ForeignKey(txnModels.Transaction)
    attitude = models.IntegerField(null=True, default=0, blank=True)
    response = models.IntegerField(null=True, default=0, blank=True)
    quality = models.IntegerField(null=True, default=0, blank=True)
    honesty = models.IntegerField(null=True, default=0, blank=True)
    content = models.TextField(null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return ' '.join([self.user.username, ':', str(self.transaction.id), str(self.create_time)])

admin.site.register(CreditPoint)
admin.site.register(CreditLog)
admin.site.register(Appraisement)
