__author__ = 'Jarvis'

import threading
import logging

from django.core.mail import send_mail, send_mass_mail, BadHeaderError
from appbid import settings

log = logging.getLogger('email')


class EmailThread(threading.Thread):
    """The new thread to send the email."""
    def __init__(self, subject, message, recipient_list, from_email=settings.EMAIL_HOST_USER, fail_silently=False):
        self.subject = subject
        self.message = message
        self.from_email = from_email
        self.recipient_list = recipient_list
        self.fail_silently = fail_silently
        threading.Thread.__init__(self)

    def run(self):
        try:
            #subject or message can not be filled.
            if isinstance(self.recipient_list, list) and len(self.recipient_list) > 0:
                send_mail(self.subject, self.message, self.from_email, self.recipient_list, self.fail_silently)
                email_str = ''
                for email in self.recipient_list:
                    email_str += email + ' '
                log.info('Send email successfully. [' + ','.join(self.recipient_list) + '] ' + self.subject)
            else:
                log.error('Email recipient_list is not correct.')
        except BadHeaderError as e:
            log.error('Send email failed. '+e.message)


class MassEmailThread(threading.Thread):
    """The new thread to send the email."""
    def __init__(self, fail_silently=False):
        self.fail_silently = fail_silently
        self.dataTuple = []
        threading.Thread.__init__(self)

    def addEmailData(self, subject, message, recipient_list, from_email=settings.EMAIL_HOST_USER):
        if isinstance(recipient_list, list) and len(recipient_list) > 0:
            self.dataTuple.append((subject, message, from_email, recipient_list))
        else:
            log.error('Email recipient_list is not correct.')

    def run(self):
        if len(self.dataTuple) > 0:
            try:
                send_mass_mail(self.dataTuple, self.fail_silently)
                log.info('Send mass email successfully.')
            except BadHeaderError as e:
                log.error('Send mass email failed. '+e.message)