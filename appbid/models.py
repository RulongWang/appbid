__author__ = 'rulongwang'
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_delete,pre_save
from django.contrib.auth.models import User
from django.contrib import admin
import os


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


class Category(models.Model):
    """Category table info."""
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class App(models.Model):
    """App table info"""
    APP_STATUS = (
        (1, 'draft'),
        (2, 'published'),
    )
    publisher = models.ForeignKey(User)
    publish_date = models.DateTimeField(null=True, blank=True)
    status = models.IntegerField(choices=APP_STATUS, null=True, blank=True, default=1)
    title = models.CharField(max_length=255, blank=True)
    category = models.ManyToManyField(Category, null=True, blank=True)
    begin_price = models.FloatField(null=True, blank=True)
    one_price = models.FloatField(null=True, blank=True)
    reserve_price = models.FloatField(null=True, blank=True)
    currency = models.ForeignKey(Currency, default=2, null=True, blank=True)
    begin_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    dl_amount = models.IntegerField(null=True, default=0, blank=True)
    revenue = models.FloatField(null=True, blank=True)
    monetize = models.ManyToManyField(Monetize, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    apple_id = models.CharField(max_length=255, null=True, blank=True)
    app_store_link = models.URLField(max_length=255, null=True, blank=True)
    minimum_bid = models.FloatField(null=True, default=1, blank=True)
    web_site = models.URLField(max_length=255, null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    last_modify = models.DateTimeField(auto_now=True)
    device = models.ManyToManyField(Device, null=True, blank=True)
    platform_version = models.CharField(max_length=255, null=True, blank=True)
    source_code = models.BooleanField(default=True)
    rating = models.CharField(max_length=5, null=True, blank=True)# rating for app

    class Meta:
        ordering = ['create_time']

    def __unicode__(self):
        return self.title


def content_file_name(instance, filename):
    """The path of saving attachment file. The pattern is publisher_id/app_id/filename"""
    return '/'.join([str(instance.app.publisher.id), str(instance.app.id), filename])


class Attachment(models.Model):
    """Attachment table info, type value:1 top images, 2 ICON, 3 PDF, 4 DOC"""
    ATTACHMENT_TYPE = (
        (1, "topImage"),
        (2, "icon"),
        (3, "pdf"),
        (4, "doc"),
    )
    app = models.ForeignKey(App)
    name = models.CharField(max_length=255, blank=True)
    type = models.IntegerField(choices=ATTACHMENT_TYPE, blank=True)
    path = models.FileField(max_length=100, upload_to=content_file_name)


@receiver(post_delete, sender=Attachment)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """Delete the file from filesystem, when corresponding 'Attachment' object is deleted."""
    if instance.path:
        if os.path.isfile(instance.path.path):
            os.remove(instance.path.path)


@receiver(pre_save, sender=Attachment)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """Delete the file from filesystem, when corresponding 'Attachment' object is changed."""
    if not instance.pk:
        return False

    try:
        old_file = Attachment.objects.get(pk=instance.pk).path
    except Attachment.DoesNotExist:
        return False

    new_file = instance.path
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


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


class PaymentItem(models.Model):
    """PaymentItem table info, include many payment items."""
    short_text = models.CharField(max_length=255)
    long_text = models.TextField()
    price = models.FloatField()
    period = models.IntegerField(default=1)# by one month
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    app = models.ManyToManyField(App)


class Gateway(models.Model):
    """Gateway table info."""
    #TODO:The fields will be discussed later.
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)


class PaymentDetail(models.Model):
    """PaymentDetail table info, the record of seller's payment detail."""
    app = models.ForeignKey(App)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    amount = models.FloatField()
    gateway = models.ForeignKey(Gateway, null=True, blank=True)
    is_payed = models.BooleanField(default=False, blank=True)


class AppInfo(models.Model):
    """AppInfo table info, include some additional info fields from apple store or somewhere else."""
    app = models.OneToOneField(App)
    price = models.FloatField(null=True, blank=True)
    icon = models.URLField(null=True, blank=True)
    track_id = models.IntegerField(null=True, blank=True)

#Need to init or edit the data by admin.
admin.site.register(Device)
admin.site.register(Currency)
admin.site.register(Monetize)
admin.site.register(Category)
admin.site.register(PaymentItem)