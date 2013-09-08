__author__ = 'rulongwang'
from django.conf.urls import patterns, include, url
from views import auth_home, register
from views import login_view,logout_view, register,account_settting,email_notification,social_connection,change_password,user_public_profile
from query.views import getDetail
urlpatterns = patterns('',
    (r'^login/$', login_view),
    (r'^logout/$', logout_view),
    (r'^register/$', register),
    (r'^home/$',auth_home),
    (r'^setting/$',account_settting),
    (r'^public_profile/$',user_public_profile),
    (r'^email_setting/$',email_notification),
    (r'^change_password/$',change_password),
    (r'^social_setting/$',social_connection),


)
