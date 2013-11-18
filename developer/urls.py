__author__ = 'rulongwang'

from django.conf.urls import patterns, url
from developer import views


urlpatterns = patterns('',
    url(r'^info/$', views.developer, name='info'),

)
