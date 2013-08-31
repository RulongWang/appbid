__author__ = 'Jarvis'

from django.conf.urls import patterns, url
from bid import views

urlpatterns = patterns('',
    url(r'^bid-create/(?P<pk>\d*)$', views.createBid, name='bid_create'),
    url(r'^bid-list/(?P<pk>\d*)$', views.getBids, name='bid_list'),
)
