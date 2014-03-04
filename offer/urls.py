__author__ = 'jia.qianpeng'

from django.conf.urls import patterns, url
from offer import views


urlpatterns = patterns('',
    url(r'^(?P<pk>\d*)$', views.registerOffer),
)