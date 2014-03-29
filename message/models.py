__author__ = 'Jarvis'

from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin


class Message(models.Model):
    TYPE = (
        (1, 'message'),
        (2, 'complain'),
        (3, 'tech'),
        (4, 'sale'),
        (5, 'advice'),
        (6, 'apply'),
    )
    title = models.CharField(max_length=255)
    content = models.TextField(null=True, blank=True)
    type = models.IntegerField(default=1)
    sender = models.ForeignKey(User, related_name='msg_sender')
    receiver = models.ForeignKey(User, related_name='msg_receiver')
    is_read = models.BooleanField(default=False, blank=True)
    submit_date = models.DateTimeField(auto_now_add=True)


def content_file_name(instance, filename):
    """The path of saving attachment file. The pattern is message/sender_id/message_id/filename"""
    return '/'.join(['message', str(instance.message.sender.id), str(instance.message.id), filename])


class Attachment(models.Model):
    """Attachment table info, type value:1 txt, 2 image, 3 pdf, 4 doc"""
    ATTACHMENT_TYPE = (
        (1, "txt"),
        (2, "image"),
        (3, "pdf"),
        (4, "doc"),
    )
    message = models.ForeignKey(Message)
    name = models.CharField(max_length=255, blank=True)
    type = models.IntegerField(choices=ATTACHMENT_TYPE, blank=True)
    path = models.FileField(max_length=255, upload_to=content_file_name)

admin.site.register(Message)
admin.site.register(Attachment)