__author__ = 'rulongwang'
from django.conf.urls import patterns, include, url
from views import auth_home, register, ajaxUserVerified
from views import login_view,logout_view, register,user_detail,email_notification,social_connection,change_password,user_public_profile,payment_account
from query.views import getDetail
urlpatterns = patterns('',
    url(r'^login/$', login_view, name='login-view'),
    url(r'^logout/$', logout_view),
    url(r'^register/$', register, name='register-view'),
    url(r'^username_verified/(?P<username>\S*)$', ajaxUserVerified, name='username-verified'),
    url(r'^email_verified/(?P<email>\w*)$', ajaxUserVerified, name='email-verified'),
    url(r'^home/$', auth_home),
    url(r'^setting/$', user_detail),
    url(r'^public_profile/$', user_public_profile),
    url(r'^email_setting/$', email_notification),
    url(r'^change_password/$', change_password),
    url(r'^social_setting/$', social_connection),
    url(r'^payrment_setting/$',payment_account),

)
