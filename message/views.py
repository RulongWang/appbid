__author__ = 'Jarvis'

import logging

from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils.translation import ugettext as _

from message import forms

log = logging.getLogger('appbid')


@csrf_protect
@transaction.commit_on_success
@login_required(login_url='/usersetting/home/')
def sendMessage(request, *args, **kwargs):
    """Send message function."""

    #For save init data
    initParam = kwargs.get('initParam')
    #Init messageForm data
    if initParam:
        initParam['messageForm'] = forms.MessageForm()
    #Save message data
    if request.method == "POST":
        messageForm = forms.MessageForm(request.POST)
        if messageForm.is_valid():
            message = messageForm.save(commit=False)
            message.is_read = False
            message.save()
            return message
        elif initParam:
            initParam['message_error'] = _('Save message failed.')
            log.error(_('Save message failed.'))
    return None

