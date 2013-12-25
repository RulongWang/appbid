__author__ = 'jia.qianpeng'

# Authentication Backends for social_auth
AUTHENTICATION_BACKENDS = (
    'social_auth.backends.twitter.TwitterBackend',
    'social_auth.backends.facebook.FacebookBackend',
    'social_auth.backends.contrib.github.GithubBackend',
    'social_auth.backends.contrib.weibo.WeiboBackend',
    'django.contrib.auth.backends.ModelBackend',
)

# SOCIAL_AUTH_PIPELINE = (
#     'social_auth.backends.pipeline.social.social_auth_user',
#     'social_auth.backends.pipeline.associate.associate_by_email',
#     'social_auth.backends.pipeline.misc.save_status_to_session',
#     'app.pipeline.redirect_to_form',
#     'app.pipeline.username',
#     'social_auth.backends.pipeline.user.create_user',
#     'social_auth.backends.pipeline.social.associate_user',
#     'social_auth.backends.pipeline.social.load_extra_data',
#     'social_auth.backends.pipeline.user.update_user_details',
# )

USE_X_FORWARDED_HOST = True
SOCIAL_AUTH_FORCE_POST_DISCONNECT = True
# SOCIAL_AUTH_REDIRECT_IS_HTTPS = True
SOCIAL_AUTH_URLOPEN_TIMEOUT = 60
SOCIAL_AUTH_UID_LENGTH = 16
SOCIAL_AUTH_ASSOCIATION_HANDLE_LENGTH = 16
SOCIAL_AUTH_NONCE_SERVER_URL_LENGTH = 16
SOCIAL_AUTH_ASSOCIATION_SERVER_URL_LENGTH = 16
SOCIAL_AUTH_ASSOCIATION_HANDLE_LENGTH = 16
#User the table saving social login user account info.
#SOCIAL_AUTH_USER_MODEL = 'auth.CustomUser'

SOCIAL_AUTH_ENABLED_BACKENDS = ('github', 'twitter', 'facebook', 'weibo',)
SOCIAL_AUTH_DEFAULT_USERNAME = 'socialauth_user'
SOCIAL_AUTH_COMPLETE_URL_NAME = 'socialauth_complete'
SOCIAL_AUTH_ASSOCIATE_URL_NAME = 'socialauth_associate_complete'

# Setup needed OAuth keys for social_auth
TWITTER_CONSUMER_KEY = 'DMKT8qzgqrgsQkOrafU5g'
TWITTER_CONSUMER_SECRET = 'ZrGdvHreXBBT3u18eJ3QiKIxCdxfaxXur1cLInseRM'
TWITTER_OAUTH_TOKEN = '1943055692-KsVP4hRY3orbfEE5Dsy6c5qh8pB093uxMDomDwg'
TWITTER_OAUTH_TOKEN_SECRET = 'fV8PZFk2kRHMcjayHmoryjT1jdb2HFfGl2EvoK0yc95XK'
FACEBOOK_APP_ID = '224844337683823'
FACEBOOK_API_SECRET = 'ecfcf5beadfb0e81061a5aa0d116c207'
GITHUB_APP_ID = '0986cfea7a082b0228e0'
GITHUB_API_SECRET = 'b628aaaa81dc0c32767ad507fb90afaf1b019270'
WEIBO_CLIENT_KEY = '863784409'
WEIBO_CLIENT_SECRET = 'a52b1ce8f0f997854d66a25c7229e100'
WEIBO_ACCESS_TOKEN = '2.00TjGl_E0bm29w0dfb95555egsLo9C'
QQ_WEIBO_API_KEY = '801433292'
QQ_WEIBO_API_SECRET = 'f5715d235167d0d20a73a83aadf2f3d9'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/auth/auth-complete/'
LOGIN_ERROR_URL = '/login-error/'