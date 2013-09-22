__author__ = 'rulongwang'

from django.conf.urls import patterns, url
from dashboard import views


urlpatterns = patterns('',
    url(r'^inbox$', views.inbox, name='inbox'),
    url(r'^sent-messages$', views.sentMessages, name='sent_messages'),
    url(r'^message-detail/(?P<pk>\d+)$', views.messageDetail, name='message_detail'),
    url(r'^create-messages/(?P<username>\S+)/(?P<pk>\d+)$', views.createMessage, name='create_message'),
)
