__author__ = 'rulongwang'

from django.db import models


class VIP(models.Model):

    name = models.CharField(max_length=100)
    cellphone = models.CharField(max_length=13, blank=True, null=True)


