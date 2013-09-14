__author__ = 'Jarvis'

from appbid import models as appModels
from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin


class ServiceItem(models.Model):
    """ServiceItem table info, include many payment items."""
    app = models.ManyToManyField(appModels.App)
    short_text = models.CharField(max_length=255)
    long_text = models.TextField()
    price = models.FloatField()
    #The period unit is month, default value 1 means one month.
    period = models.IntegerField(default=1)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_basic_service = models.BooleanField(default=False)

    def __unicode__(self):
        return self.short_text


class ServiceDetail(models.Model):
    """ServiceDetail table info, the record of seller's payment detail."""
    app = models.ForeignKey(appModels.App)
    #The start date is publish date, and set the date when verify app or pay.
    start_date = models.DateTimeField(null=True, blank=True)
    #The default interval is 30 days, and set.the date when verify app or pay.
    end_date = models.DateTimeField(null=True, blank=True)
    #The actual amount means the amount after using discount_rate.
    actual_amount = models.FloatField(null=True, blank=True)
    amount = models.FloatField(null=True, blank=True)
    is_payed = models.BooleanField(default=False, blank=True)


class Gateway(models.Model):
    """Gateway table info - support paypal, alipay now."""
    #TODO:The fields will be discussed later.
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)


class Account(models.Model):
    """Account table info."""
    ACCOUNT_TYPE = (
        (1, 'paypal'),
        (2, 'alipay'),
    )
    user = models.ForeignKey(User)
    type = models.IntegerField(choices=ACCOUNT_TYPE)
    value = models.EmailField()


class AccountAdmin(admin.ModelAdmin):
    """The set of Account table displaying in admin page."""
    list_display = ('user', 'type', 'value')


admin.site.register(ServiceItem)
admin.site.register(Account, AccountAdmin)