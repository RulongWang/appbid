__author__ = 'rulongwang'

from django.conf.urls import patterns, url
from usersetting import views


urlpatterns = patterns('',
    url(r'^login/$', views.loginView, name='login_view'),
    url(r'^logout/$', views.logoutView, name='logout_view'),
    url(r'^register/$', views.register, name='register_view'),
    url(r'^username-verified/(?P<username>\S*)$', views.ajaxUserVerified, name='username_verified'),
    url(r'^email-verified/(?P<email>\w*)$', views.ajaxUserVerified, name='email_verified'),
    url(r'^register-active/(?P<username>\S+)/(?P<pk>\d+)$', views.registerActive, name='register_active'),
    #https://github.com/users/jarvisjia/emails/5800727/confirm_verification/2cd4ea255dd3e1deae130868d75cfa28fc423034
    url(r'^(?P<username>\S+)/emails/(?P<pk>\d+)/confirm_verification/(?P<confirm_token>\w+)$', views.registerActiveConfirm, name='register_active_confirm'),
    url(r'^home/$', views.authHome, name='home'),
    url(r'^user-detail$', views.userDetail, name='user_detail'),
    url(r'^public-profile$', views.userPublicProfile, name='public_profile'),
    url(r'^subscription-setting$', views.subscriptionSetting, name='subscription_setting'),
    url(r'^change-password$', views.changePassword, name='change_password'),
    url(r'^security-setting$', views.securitySetting, name='security_setting'),
    url(r'^security-setting-email$', views.securitySettingEmail, name='security_setting_email'),
    url(r'^security-setting-email-confirm$', views.securitySettingEmailConfirm, name='security_setting_email_confirm'),
    url(r'^security-setting-phone$', views.securitySettingPhone, name='security_setting_phone'),
    url(r'^security-setting-phone-confirm$', views.securitySettingPhoneConfirm, name='security_setting_phone_confirm'),
    url(r'^social-setting$', views.socialConnection, name='social_setting'),
    url(r'^payment-setting$', views.paymentAccount, name='payment_setting'),
)
