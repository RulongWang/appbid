__author__ = 'rulongwang'
from django.conf.urls import patterns, include, url
from auth.views import auth_home
from auth.views import login_view,logout_view
urlpatterns = patterns('',
    (r'login/$', login_view),
    (r'logout/$', logout_view),
    (r'home/$',auth_home),
)
