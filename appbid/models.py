__author__ = 'rulongwang'
from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin


class Device(models.Model):
    """Device table info, device value: iPad, iPhone, iTouch, iWatch"""
    device = models.CharField(max_length=255)

    def __unicode__(self):
        return self.device


class Currency(models.Model):
    """Currency table info, currency value: CNY, USD"""
    currency = models.CharField(max_length=20)

    def __unicode__(self):
        return self.currency


class Monetize(models.Model):
    """Monetize table info, method value: advertisement, software sale"""
    method = models.CharField(max_length=255)

    def __unicode__(self):
        return self.method


class App(models.Model):
    """App table info"""
    APP_STATUS = (
        (1, 'draft'),
        (2, 'published'),

    )
    publisher = models.ForeignKey(User)
    publish_date = models.DateTimeField(null=True, blank=True)
    status = models.IntegerField(choices=APP_STATUS, default=1)
    title = models.CharField(max_length=255)
    begin_price = models.FloatField(null=True, blank=True)
    one_price = models.FloatField(null=True, blank=True)
    reserve_price = models.FloatField(null=True, blank=True)
    currency = models.ForeignKey(Currency,default='USD', null=True, blank=True)
    begin_date = models.DateTimeField()
    end_date = models.DateTimeField()
    dl_amount = models.IntegerField(default=0,null=True,blank=True)
    revenue = models.FloatField(null=True, blank=True)
    monetize = models.ManyToManyField(Monetize)
    description = models.TextField()
    app_store_link = models.CharField(max_length=255, null=True, blank=True)

    minimum_bid = models.FloatField(default=1)
    web_site = models.URLField(max_length=255, null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    last_modify = models.DateTimeField(auto_now=True)
    device = models.ManyToManyField(Device)
    platform_version = models.CharField(max_length=255)
    source_code = models.BooleanField(default=True)
    step = models.IntegerField(default=0,null=False,blank=False)

    class Meta:
        ordering = ['create_time']


class Attachment(models.Model):
    """Attachment table info, type value:1 top images, 2 ICON, 3 PDF, 4 DOC"""
    ATTACHMENT_TYPE = (
        (1, "topImage"),
        (2, "icon"),
        (3, "pdf"),
        (4, "doc"),
    )
    app = models.ForeignKey(App)
    name = models.CharField(max_length=255)
    type = models.IntegerField(choices=ATTACHMENT_TYPE)
    path = models.CharField(max_length=255)


class Bidding(models.Model):
    """Bidding table info, status value: 1 approved, 2 rejected, 3 inProgress"""
    BIDDING_STATUS = (
        (1, "approved"),
        (2, "rejected"),
        (3, "inProgress"),
    )
    app = models.ForeignKey(App)
    price = models.FloatField()
    comment = models.CharField(max_length=255)
    buyer = models.ManyToManyField(User)
    bid_time = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=BIDDING_STATUS, default=3)


admin.site.register(App)
admin.site.register(Attachment)