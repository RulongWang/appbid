__author__ = 'rulongwang'
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """UserProfile table info."""
    user = models.OneToOneField(User)
    is_bid_approved = models.BooleanField(default=False)


class UserDetails(models.Model):

    user = models.OneToOneField(User)
    thumbnail = models.FilePathField(blank=True)
    birthday = models.DateTimeField(blank=True)
    gender = models.BooleanField(blank=True)
    homepage = models.CharField(blank=True)
    real_name = models.CharField(blank=True,max_length=100)
    street_address = models.CharField(blank=True,max_length=300)
    city = models.CharField(blank=True,max_length=100)
    state_provience = models.CharField(blank=True, max_length=100)
    post_code = models.CharField(blank=True, max_length=10)
    country = models.CharField(blank=True,max_length=100)
    email = models.EmailField(blank=True)

class account(models.Model):
    #account,paypal or alipay
    account_type = (
        (1,'paypal'),
        (2,'alipay'),
    )
    user = models.OneToOneField(User)
    type = models.IntegerField(account_type)
    value = models.EmailField()


class email_items(models.Model):
    # email notification
    item = models.CharField(max_length=200)


class email_setting(models.Model):
    user = models.ManyToManyField(User)
    setting_item = models.ForeignKey(email_items)
    value = models.BooleanField()











