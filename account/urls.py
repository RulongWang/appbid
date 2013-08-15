__author__ = 'rulongwang'
from django.conf.urls import patterns, include, url
from account.views import auth_home
from account.views import login_view,logout_view
urlpatterns = patterns('',
    (r'login/$', login_view),
    (r'logout/$', logout_view),
    (r'home/$',auth_home),
)
