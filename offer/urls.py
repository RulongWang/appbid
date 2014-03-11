__author__ = 'jia.qianpeng'

from django.conf.urls import patterns, url
from offer import views


urlpatterns = patterns('',
    url(r'^job/(?P<pk>\d*)$', views.registerOffer, name='offer_create'),
    url(r'^job-detail/(?P<pk>\d+)$', views.offerDetail, name='offer_detail'),
    url(r'^job-list$', views.offerList, name='offer_list'),
    url(r'^my-job-list$', views.myOfferList, name='my_offer_list'),
)