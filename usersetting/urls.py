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
    url(r'^(?P<username>\S+)/emails/(?P<pk>\d+)/register-confirm-verification/(?P<confirm_token>\w+)$',
        views.registerActiveConfirm, name='register_active_confirm'),
    url(r'^home/$', views.authHome, name='home'),

    url(r'^security-verification-password$', views.securityVerification,
        {'current': 'usersetting:change_password',
         'saveMethod': views.changePassword,
        }, name='security_verification_password'),
    url(r'^security-verification-email$', views.securityVerification,
        {'current': 'usersetting:security_setting_email',
         'saveMethod': views.securitySettingEmail,
        }, name='security_verification_email'),
    url(r'^security-verification-phone$', views.securityVerification,
        {'current': 'usersetting:security_setting_phone',
         'saveMethod': views.securitySettingPhone,
        }, name='security_verification_phone'),
    url(r'^security-verification-payment$', views.securityVerification,
        {'current': 'usersetting:payment_setting',
         'saveMethod': views.paymentAccount,
        }, name='security_verification_payment'),
    url(r'^send-pin$', views.sendPIN, name='send_PIN'),

    url(r'^user-detail$', views.userDetail, name='user_detail'),
    url(r'^public-profile$', views.userPublicProfile, name='public_profile'),
    url(r'^subscription-setting$', views.subscriptionSetting, name='subscription_setting'),
    url(r'^change-password$', views.changePassword, name='change_password'),
    url(r'^security-setting$', views.securitySetting, name='security_setting'),

    url(r'^security-setting-email$', views.securitySettingEmail, name='security_setting_email'),
    url(r'^security-setting-email-update$', views.securitySettingEmailUpdate, name='security_setting_email_update'),
    url(r'^(?P<username>\S+)/emails/(?P<pk>\d+)/email_security_verification/(?P<confirm_token>\w+)$',
        views.securitySettingEmailConfirm, name='security_setting_email_confirm'),
    url(r'^security-setting-phone$', views.securitySettingPhone, name='security_setting_phone'),

    url(r'^social-setting$', views.socialConnection, name='social_setting'),
    url(r'^payment-setting/(?P<next>\S*)$', views.paymentAccount, name='payment_setting'),
)
