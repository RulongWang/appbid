__author__ = 'Jarvis'

from django.core.mail import send_mail, send_mass_mail
from appbid import models, settings
import common


def sentEmail():
    send_mail('Subject here', 'Here is message', '****@gmail.com', ['****@163.com'])
    print 'Send email'


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



