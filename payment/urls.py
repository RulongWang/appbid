__author__ = 'Jarvis'

from django.conf.urls import patterns, url
from payment import views

urlpatterns = patterns('',
    url(r'^payment/(?P<app_id>\d+)/(?P<service_id>\d+)/(?P<service_sn>\d+)$', views.payment, name='payment'),
    url(r'^paypal_return/$', views.paypalreturn, name='paymentreturn'),
    url(r'^paypal_cancel/$', views.paymentcancel, name='paymentcancel'),

)