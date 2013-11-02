__author__ = 'rulongwang'

from django.conf.urls import patterns, url
from help import views as helpviews


urlpatterns = patterns('',
    url(r'^guide/$', helpviews.guide, name='guide'),
    url(r'^pricing/$', helpviews.pricing, name='pricing'),
    url(r'^support/$', helpviews.support, name='support'),
    url(r'^privacy/$', helpviews.privacy, name='privacy'),
    url(r'^terms/$', helpviews.terms, name='terms'),
    url(r'^security/$', helpviews.security, name='security'),
    url(r'^contact/$', helpviews.contact, name='contact'),
    url(r'^about/$', helpviews.about, name='about'),
)
