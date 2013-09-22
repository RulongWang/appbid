__author__ = 'Jarvis'

from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils.translation import ugettext as _

from message import forms


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
            message.type = 1
            message.save()
            return message
        elif initParam:
            initParam['message_error'] = _('Send private message failed.')
    return None

