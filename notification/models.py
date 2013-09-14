__author__ = 'Jarvis'
from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin


class NotificationTemplate(models.Model):
    """NotificationTemplate table info."""
    NOTIFICATION_TYPE = (
        (1, 'EMAIL'),
        (2, 'SMS'),
    )
    LANGUAGES = (
        (1, 'EN'),
        (2, 'ZH'),
    )
    name = models.CharField(max_length=255)
    language = models.IntegerField(choices=LANGUAGES, default=1)
    type = models.IntegerField(choices=NOTIFICATION_TYPE, default=1)
    template = models.TextField(null=True)
    description = models.TextField(null=True, blank=True)
    version = models.CharField(max_length=255, null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    last_modify = models.DateTimeField(auto_now=True)
    modifier = models.OneToOneField(User)


class NotificationTemplateAdmin(admin.ModelAdmin):
    """The set of NotificationTemplate table displaying in admin page."""
    list_display = ('name', 'language', 'type', 'template', 'description', 'version')


#Need to init or edit the data by admin.
admin.site.register(NotificationTemplate, NotificationTemplateAdmin)