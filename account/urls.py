__author__ = 'rulongwang'
from django.conf.urls import patterns, url
from account import views
urlpatterns = patterns('',
    url(r'^login/$', views.login_view, name='login-view'),
    url(r'^logout/$', views.logout_view),
    url(r'^register/$', views.register, name='register-view'),
    url(r'^username_verified/(?P<username>\S*)$', views.ajaxUserVerified, name='username-verified'),
    url(r'^email_verified/(?P<email>\w*)$', views.ajaxUserVerified, name='email-verified'),
    url(r'^register_active/(?P<username>\S+)/(?P<pk>\d+)$', views.register_active, name='register-active'),
    #https://github.com/users/jarvisjia/emails/5800727/confirm_verification/2cd4ea255dd3e1deae130868d75cfa28fc423034
    url(r'^(?P<username>\S+)/emails/(?P<pk>\d+)/confirm_verification/\w{30}$', views.account_active_by_email, name='account-active-by-email'),
    url(r'^home/$', views.auth_home),
    url(r'^setting/$', views.userDetail),
    url(r'^public_profile/$', views.user_public_profile),
    url(r'^email_setting/$', views.email_notification),
    url(r'^change_password/$', views.change_password),
    url(r'^social_setting/$', views.social_connection),
    url(r'^payment_setting/$',views.payment_account),

)
