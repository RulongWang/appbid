__author__ = 'Jarvis'

from django.db import models
from django.contrib.auth.models import User
from appbid import models as appModels
from payment import models as paymentModels

SELLER_STATUS = (
    (1, 'Unsold'),
    (2, 'Waiting for payment'),
    (3, 'In delivery'),
    (4, 'Waiting for evaluation'),
    (5, 'Closed'),
)

BUYER_STATUS = (
    (1, 'Initialized'),
    (2, 'Pay it now'),
    (3, 'Waiting for delivery'),
    (4, 'Waiting for evaluation'),
    (5, 'Closed'),
)


class Transaction(models.Model):
    STATUS = (
        (1, 'Initialized'),
        (2, 'Unpaid'),
        (3, 'Delivery'),
        (4, 'Evaluation'),
        (5, 'Closed'),
    )
    BUY_TYPE = (
        (1, 'one-price-buy'),
        (2, 'bid-win'),
    )
    app = models.OneToOneField(appModels.App)
    status = models.IntegerField(choices=STATUS, default=1)
    seller = models.ForeignKey(User, null=True, related_name='txn_seller')
    buyer = models.ForeignKey(User, null=True, related_name='txn_buyer')
    price = models.FloatField(null=True)
    end_time = models.DateTimeField(null=True)
    create_time = models.DateTimeField(auto_now_add=True)

    #For user pay.
    buy_type = models.IntegerField(choices=BUY_TYPE, null=True)
    seller_price = models.FloatField(null=True)
    appswalk_price = models.FloatField(null=True)
    gateway = models.ForeignKey(paymentModels.Gateway, null=True)
    buyer_account = models.CharField(max_length=255, null=True)
    seller_account = models.CharField(max_length=255, null=True)
    appswalk_account = models.CharField(max_length=255, null=True)
    pay_key = models.CharField(max_length=255, null=True)


class TransactionLog(models.Model):
    STATUS = (
        (1, 'unsold'),
        (2, 'trade'),
        (3, 'paid'),
        (4, 'closed'),
    )
    BUY_TYPE = (
        (1, 'one-price-buy'),
        (2, 'bid-win'),
    )
    app = models.ForeignKey(appModels.App)
    status = models.IntegerField(choices=STATUS)
    seller = models.ForeignKey(User, null=True, related_name='txn_log_seller')
    buyer = models.ForeignKey(User, null=True, related_name='txn_log_buyer')
    price = models.FloatField(null=True)
    seller_price = models.FloatField(null=True)
    appswalk_price = models.FloatField(null=True)
    buy_type = models.IntegerField(choices=BUY_TYPE, null=True)
    gateway = models.ForeignKey(paymentModels.Gateway, null=True)
    buyer_account = models.CharField(max_length=255, null=True)
    seller_account = models.CharField(max_length=255, null=True)
    appswalk_account = models.CharField(max_length=255, null=True)
    pay_key = models.CharField(max_length=255, null=True)
    create_time = models.DateTimeField(auto_now_add=True)


class CreditRating(models.Model):
    app = models.ForeignKey(appModels.App)
    rator = models.ForeignKey(User, related_name='credit_rating_rator')
    target = models.ForeignKey(User, related_name='credit_rating_target')
    level = models.IntegerField(default=5)
    content = models.TextField(null=True)
    create_time = models.DateTimeField(auto_now_add=True)