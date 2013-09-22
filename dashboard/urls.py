__author__ = 'rulongwang'

from django.conf.urls import patterns, url
from dashboard import views


urlpatterns = patterns('',
    url(r'^inbox$', views.inbox, name='inbox'),
    url(r'^sent-messages$', views.sentMessages, name='sent_messages'),
    url(r'^message-detail/(?P<msg_action>\w+)/(?P<msg_id>\d+)$', views.messageDetail, name='message_detail'),
    url(r'^create-message/(?P<msg_action>\w+)/(?P<username>\S+)/(?P<user_id>\d+)/(?P<msg_id>\d+)$', views.createMessage, name='create_message'),
)
