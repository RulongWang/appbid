__author__ = 'rulongwang'

from django.conf.urls import patterns, url
from home import views


urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),
    url(r'^screw-home$', views.screwHome, name='screw_home'),
)
