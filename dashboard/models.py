__author__ = 'Jarvis'

from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from appbid import models as appModels


class WatchApp(models.Model):
    """Watch App"""
    app = models.ForeignKey(appModels.App)
    buyer = models.ForeignKey(User)


class WatchCategory(models.Model):
    """Watch Category"""
    category = models.ForeignKey(appModels.Category)
    buyer = models.ForeignKey(User)


class WatchSeller(models.Model):
    """Watch publisher"""
    seller = models.ForeignKey(User, related_name='watch_seller')
    buyer = models.ForeignKey(User, related_name='watch_buyer')

admin.site.register(WatchApp)
admin.site.register(WatchCategory)
admin.site.register(WatchSeller)