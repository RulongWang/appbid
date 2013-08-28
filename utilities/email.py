__author__ = 'Jarvis'
from django.core.mail import send_mail


def sentEmail():
    send_mail('Subject here', 'Here is message', '****@gmail.com', ['****@163.com'])
    print 'Send email'