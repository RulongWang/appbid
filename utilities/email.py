__author__ = 'Jarvis'

import threading

from django.core.mail import send_mail, send_mass_mail
from appbid import models, settings
import common


def sentEmail(*args, **kwargs):
    """Sent email"""
    subject = kwargs.get('subject')
    message = kwargs.get('message')
    from_email = kwargs.get('from_email', None)
    if from_email is None:
        from_email = settings.EMAIL_HOST_USER
    recipient_list = kwargs.get('recipient_list')
    fail_silently = kwargs.get('fail_silently')
    if fail_silently is None:
        fail_silently = False
    if subject and message and recipient_list:
        send_mail(subject, message, from_email, recipient_list)
    else:
        print 'do it later, log error info.'


def verificationAppJob(*args, **kwargs):
    """Do the job of verified app owner ship on schedule plan"""
    emailData = []
    ownerShipScans = models.OwnerShip_Scan.objects.all()
    for ownerShipScan in ownerShipScans:
        app = ownerShipScan.app
        result = common.getITunes(app.apple_id)
        if result is None:
            continue
        description = result.get('description', None)
        if app.verify_token in description:
            #TODO: fill in the subject and message of the success email template for first, second parameter.
            emailData.append((app.title, app.description, settings.EMAIL_HOST_USER, [app.publisher.email]))
        else:
            #TODO: fill in the subject and message of the failed email template for first, second parameter.
            emailData.append((app.title, app.description, settings.EMAIL_HOST_USER, [app.publisher.email]))
    if emailData:
        try:
            send_mass_mail(emailData)
            ownerShipScans.delete()
            print 'Send email successfully.'
        except:
            #TODO:write the exception to file or database.
            raise 'Send email failure.'


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
            sentEmail(subject=self.subject, message=self.message, recipient_list=self.recipient_list,
                      from_email=self.from_email, fail_silently=self.fail_silently)
        except:
            #TODO:log the error message.
            print 'Send email failed.'


class MassEmailThread(threading.Thread):
    """The new thread to send the email."""
    def __init__(self, subject, message, recipient_list, from_email=settings.EMAIL_HOST_USER, fail_silently=False):
        self.subject = subject
        self.message = message
        self.from_email = from_email
        self.recipient_list = recipient_list
        self.fail_silently = fail_silently
        threading.Thread.__init__(self)

    def run(self):
        print 'Send mass mail.'#TODO:to do it later.
        # send_mass_mail(subject=self.subject, message=self.message, recipient_list=self.recipient_list,
        #           from_email=self.from_email, fail_silently=self.fail_silently)



