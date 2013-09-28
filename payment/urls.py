__author__ = 'Jarvis'

from django.conf.urls import patterns, url
from payment import views

urlpatterns = patterns('',
    url(r'^payment/(?P<app_id>\d+)/(?P<service_id>\d+)$', views.payment, name='payment'),
)