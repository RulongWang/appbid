__author__ = 'rulongwang'

from django.conf.urls import patterns, url
from home import views
from help import views as helpView


urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),
    url(r'^termsandconditions$',helpView.terms,name='terms'),
    url(r'^screw-home$', views.screwHome, name='screw_home'),
)
