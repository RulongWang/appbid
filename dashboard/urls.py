__author__ = 'rulongwang'

from django.conf.urls import patterns, url
from dashboard import views


urlpatterns = patterns('',
    url(r'^activity/$', views.activity, name='dashboard'),

)
