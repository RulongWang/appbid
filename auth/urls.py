__author__ = 'Jarvis'

from django.conf.urls import patterns, url
from auth import views

urlpatterns = patterns('',
    url(r'^auth-complete/$', views.authComplete, name='auth_complete'),
    url(r'^auth-error/$', views.authError, name='auth_error'),
)
