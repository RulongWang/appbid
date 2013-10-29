__author__ = 'Jarvis'


from django.conf.urls import patterns, url
from order import views

urlpatterns = patterns('',
    url(r'^checkout/(?P<app_id>\d+)/(?P<service_id>\d+)/(?P<service_sn>\d+)$', views.checkout,
        #The needed operation method in payment.
        {'executeMethod': views.updateServiceDetail,
        }, name='checkout'),
)