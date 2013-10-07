__author__ = 'Jarvis'

from django.conf.urls import patterns, url
from transaction import views


urlpatterns = patterns('',
    url(r'^trade-now/(?P<app_id>\w+)/(?P<buyer_id>\w+)/(?P<bid_id>\w+)', views.tradeNow, name='trade_now'),
    url(r'^trade-action/(?P<action>\w+)/(?P<app_id>\w+)/(?P<user_id>\w+)', views.tradeAction, name='trade_action'),
)
