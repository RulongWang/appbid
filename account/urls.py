__author__ = 'rulongwang'

from django.conf.urls import patterns, url
from account import views


urlpatterns = patterns('',
    url(r'^login/$', views.loginView, name='login_view'),
    url(r'^logout/$', views.logoutView),
    url(r'^register/$', views.register, name='register_view'),
    url(r'^username-verified/(?P<username>\S*)$', views.ajaxUserVerified, name='username_verified'),
    url(r'^email-verified/(?P<email>\w*)$', views.ajaxUserVerified, name='email_verified'),
    url(r'^register-active/(?P<username>\S+)/(?P<pk>\d+)$', views.registerActive, name='register_active'),
    #https://github.com/users/jarvisjia/emails/5800727/confirm_verification/2cd4ea255dd3e1deae130868d75cfa28fc423034
    url(r'^(?P<username>\S+)/emails/(?P<pk>\d+)/confirm_verification/\w{30}$', views.accountActiveByEmail, name='account_active_by_email'),
    url(r'^home/$', views.authHome),
    url(r'^setting/$', views.userDetail),
    url(r'^public-profile/$', views.userPublicProfile),
    url(r'^subscription-setting/$', views.subscriptionSetting),
    url(r'^change-password/$', views.changePassword),
    url(r'^social-setting/$', views.socialConnection),
    url(r'^payment-setting/$',views.paymentAccount),

)
