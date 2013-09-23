__author__ = 'Jarvis'

from django.db import models
from django.contrib.auth.models import User


class Message(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField(null=True, blank=True)
    type = models.IntegerField(default=1, blank=True)#use later.
    sender = models.ForeignKey(User, related_name='msg_sender')
    receiver = models.ForeignKey(User, related_name='msg_receiver')
    is_read = models.BooleanField(default=False, blank=True)
    submit_date = models.DateTimeField(auto_now_add=True)

