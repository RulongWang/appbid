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
TWITTER_CONSUMER_KEY = 'YecmHUI9uEPF8gpCHliQ'
TWITTER_CONSUMER_SECRET = 'R9yMWVriMxsoBvhIO6guDiQLEIYXW7wcT2bHimjS7Y'
TWITTER_OAUTH_TOKEN = '190863127-ghzIMgobp7BQvTN6hvmWbTt4qmBFgiw2zRJN1FH0'
TWITTER_OAUTH_TOKEN_SECRET = '8eLuXG2b99nd31GbWsiA6mjTleaphN8UNmvuFQt4H0'
FACEBOOK_APP_ID = '224844337683823'
FACEBOOK_API_SECRET = 'ecfcf5beadfb0e81061a5aa0d116c207'
GITHUB_APP_ID = '0986cfea7a082b0228e0'
GITHUB_API_SECRET = 'b628aaaa81dc0c32767ad507fb90afaf1b019270'
WEIBO_CLIENT_KEY = '2913621266'
WEIBO_CLIENT_SECRET = '2649e7be854f444662400be63b8ee754'
WEIBO_ACCESS_TOKEN = '2.00k2kaSB5zPLLDe61c5e4ed1DVX24B'
QQ_WEIBO_API_KEY = '801433292'
QQ_WEIBO_API_SECRET = 'f5715d235167d0d20a73a83aadf2f3d9'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/auth/auth-complete/'
LOGIN_ERROR_URL = '/login-error/'