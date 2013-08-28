__author__ = 'rulongwang'
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """UserProfile table info."""
    user = models.OneToOneField(User)
    is_bid_approved = models.BooleanField(default=False)