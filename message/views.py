__author__ = 'Jarvis'
from message import forms


def sendMessage(request, *args, **kwargs):
    """Message function"""
    initParam = kwargs.get('initParam')#For save init data

    if initParam:#Init messageForm data
        messageForm = forms.MessageForm()
        initParam['messageForm'] = messageForm
    else:#Save message data
        if request.method == "POST":
            messageForm = forms.MessageForm(request.POST)
            if messageForm.is_valid():
                message = messageForm.save(commit=False)
                message.type = 1
                message.save()

