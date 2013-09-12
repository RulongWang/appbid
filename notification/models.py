__author__ = 'Jarvis'
from django.db import models


class NotificationTemplate(models.Model):
    language = models.CharField(max_length=255)