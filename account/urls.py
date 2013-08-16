__author__ = 'rulongwang'
from django.conf.urls import patterns, include, url
from account.views import auth_home, register
from account.views import login_view,logout_view, register
urlpatterns = patterns('',
    (r'login/$', login_view),
    (r'logout/$', logout_view),
    (r'^register/$', register),
    (r'home/$',auth_home),
)
