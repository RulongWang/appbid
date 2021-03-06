__author__ = 'Jarvis'

from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin


class Gateway(models.Model):
    """Gateway table info - support paypal, alipay now."""
    name = models.CharField(max_length=255)
    logo = models.CharField(max_length=255)
    description = models.TextField(null=True)
    is_active = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class GatewayAdmin(admin.ModelAdmin):
    """The set of Account table displaying in admin page."""
    list_display = ('name', 'logo', 'description', 'is_active')


class AcceptGateway(models.Model):
    """AcceptGateway table info."""
    user = models.ForeignKey(User)
    type = models.ForeignKey(Gateway)
    value = models.EmailField()
    is_active = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False, blank=True)


class AcceptGatewayAdmin(admin.ModelAdmin):
    """The set of Account table displaying in admin page."""
    list_display = ('user', 'type', 'value')


admin.site.register(Gateway, GatewayAdmin)
admin.site.register(AcceptGateway, AcceptGatewayAdmin)