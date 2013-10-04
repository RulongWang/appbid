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
    seller = models.ForeignKey(User)
    buyer = models.ForeignKey(User)
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
    seller = models.ForeignKey(User, null=True)
    buyer = models.ForeignKey(User, null=True)
    price = models.FloatField(null=True)
    create_time = models.DateTimeField(auto_now_add=True)


class Evaluation(models.Model):
    app = models.ForeignKey(appModels.App)
    sender = models.ForeignKey(User, related_name='msg_sender')
    receiver = models.ForeignKey(User, related_name='msg_receiver')
    level = models.IntegerField(default=5)
    content = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)