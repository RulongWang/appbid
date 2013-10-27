__author__ = 'Jarvis'

from django.db import models
from django.contrib import admin


class SystemParam(models.Model):
    """Config the system parameter."""
    key = models.CharField(max_length=255)
    value = models.TextField()
    description = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return ' '.join([self.key, ':', self.value, '', self.description])


class Job(models.Model):
    """Job table info - Running many kinds of regular jobs."""
    job_name = models.CharField(max_length=255)
    begin_time = models.DateTimeField()
    end_time = models.DateTimeField()
    description = models.TextField(null=True, blank=True)

admin.site.register(SystemParam)
admin.site.register(Job)
