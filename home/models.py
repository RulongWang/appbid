from django.db import models
from django.contrib import sites

# Create your models here.


class VIP(models.Model):

    name = models.CharField(max_length=100)
    cellphone = models.CharField(max_length=13, blank=True, null=True)


