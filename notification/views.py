__author__ = 'Jarvis'

import random
import string

from notification import models
from utilities import email
from utilities import common


def sendRegisterActiveEmail(request, *args, **kwargs):
    """After user register, send the account active link to his email."""
    user = kwargs.get('user', None)
    if user is None:
        return None
    if request.is_secure():
        link_header = ''.join(['https://', request.META.get('HTTP_HOST')])
    else:
        link_header = ''.join(['http://', request.META.get('HTTP_HOST')])
    length = common.getSystemParam(key='active_link_confirm_token_length', default=30)
    token = ''.join(random.sample(string.ascii_letters+string.digits, string.atoi(length)))
    #TODO:user id or other value, we will discuss it.
    active_link = '/'.join([link_header, 'usersetting', user.username, 'emails', str(user.id), 'register-confirm-verification', token])

    templates = models.NotificationTemplate.objects.filter(name='register_active')
    if templates:
        subject = templates[0].subject
        template = templates[0].template.replace('{username}', user.username).replace('{active_link}', active_link)
        recipient_list = [user.email]
        email.sentEmail(subject=subject, message=template, recipient_list=recipient_list)


def sendSecurityVerificationEmail(request, *args, **kwargs):
    """After user update email in security setting, send the email verification link to the new email."""
    user = kwargs.get('user', None)
    if user is None:
        return None
    if request.is_secure():
        link_header = ''.join(['https://', request.META.get('HTTP_HOST')])
    else:
        link_header = ''.join(['http://', request.META.get('HTTP_HOST')])
    length = common.getSystemParam(key='active_link_confirm_token_length', default=30)
    token = ''.join(random.sample(string.ascii_letters+string.digits, string.atoi(length)))
    #TODO:user id or other value, we will discuss it.
    active_link = '/'.join([link_header, 'usersetting', user.username, 'emails', str(user.id), 'email_security_verification', token])

    templates = models.NotificationTemplate.objects.filter(name='email_security_verification')
    if templates:
        subject = templates[0].subject
        template = templates[0].template.replace('{username}', user.username).replace('{active_link}', active_link)
        recipient_list = [user.email]
        email.sentEmail(subject=subject, message=template, recipient_list=recipient_list)
