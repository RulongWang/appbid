__author__ = 'Jarvis'

import random
import string

from notification import models
from utilities import email
from system import models as systemModels


def sendRegisterActiveEmail(request, *args, **kwargs):
    user = kwargs.get('user', None)
    if user is None:
        return None
    if request.is_secure():
        link_header = ''.join(['https://', request.META.get('HTTP_HOST')])
    else:
        link_header = ''.join(['http://', request.META.get('HTTP_HOST')])
    service_expiry_date = systemModels.SystemParam.objects.filter(key='active_link_confirm_token_length')
    if service_expiry_date:
        length = string.atoi(service_expiry_date[0].value)
    else:
        length = 30
    token = ''.join(random.sample(string.ascii_letters+string.digits, length))
    #TODO:user id or other value, we will discuss it.
    active_link = '/'.join([link_header, 'usersetting', user.username, 'emails', str(user.id), 'confirm_verification', token])

    templates = models.NotificationTemplate.objects.filter(name='register-active')
    if templates:
        subject = templates[0].subject
        template = templates[0].template.replace('{username}', user.username).replace('{active_link}', active_link)
        recipient_list = [user.email]
        email.sentEmail(subject=subject, message=template, recipient_list=recipient_list)
