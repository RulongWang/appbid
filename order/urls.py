__author__ = 'Jarvis'


from django.conf.urls import patterns, url
from order import views

urlpatterns = patterns('',
    url(r'^checkout/(?P<app_id>\d+)/(?P<service_id>\d+)/(?P<service_sn>\d+)$', views.checkout, name='checkout'),
    url(r'^buyer-pay/(?P<app_id>\d+)/(?P<service_id>\d+)/(?P<token>\w+)$', views.buyerPay, name='buyer_pay'),
)