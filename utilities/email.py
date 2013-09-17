__author__ = 'Jarvis'

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



