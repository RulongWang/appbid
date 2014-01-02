__author__ = 'Jarvis'

from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from appbid import models as appModels


class Bidding(models.Model):
    """Bidding table info, status value: 1 approved, 2 rejected, 3 inProgress"""
    BIDDING_STATUS = (
        (1, "approved"),
        (2, "rejected"),
        (3, "pending"),
    )
    app = models.ForeignKey(appModels.App)
    price = models.FloatField()
    comment = models.TextField(null=True, blank=True)
    buyer = models.ForeignKey(User)
    bid_time = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=BIDDING_STATUS, null=True, blank=True, default=3)

#Need to init or edit the data by admin.
admin.site.register(Bidding)