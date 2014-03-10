__author__ = 'jia.qianpeng'

from django.conf.urls import patterns, url
from offer import views


urlpatterns = patterns('',
    url(r'^offer/(?P<pk>\d*)$', views.registerOffer, name='offer'),
    url(r'^offer-detail/(?P<pk>\d+)$', views.offerDetail, name='offer_detail'),
)