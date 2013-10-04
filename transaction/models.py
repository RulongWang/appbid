__author__ = 'Jarvis'

from django.db import models
from django.contrib.auth.models import User
from appbid import models as appModels


class Transaction(models.Model):
    STATUS = (
        (1, 'Unsold'),
        (2, 'Unpaid'),
        (3, 'Transaction'),
        (4, 'Closed'),
    )
    app = models.OneToOneField(appModels.App)
    status = models.IntegerField(choices=STATUS, default=1)
    seller = models.ForeignKey(User, related_name='txn_seller')
    buyer = models.ForeignKey(User, related_name='txn_buyer')
    price = models.FloatField()
    end_time = models.DateTimeField(null=True)


class TransactionLog(models.Model):
    STATUS = (
        (1, 'trade'),
        (2, 'paid'),
        (3, 'closed'),
    )
    app = models.ForeignKey(appModels.App)
    status = models.IntegerField(choices=STATUS)
    seller = models.ForeignKey(User, null=True, related_name='txn_log_seller')
    buyer = models.ForeignKey(User, null=True, related_name='txn_log_buyer')
    price = models.FloatField(null=True)
    create_time = models.DateTimeField(auto_now_add=True)


class CreditRating(models.Model):
    app = models.ForeignKey(appModels.App)
    rator = models.ForeignKey(User, related_name='credit_rating_rator')
    target = models.ForeignKey(User, related_name='credit_rating_target')
    level = models.IntegerField(default=5)
    content = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)