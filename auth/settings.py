__author__ = 'jia.qianpeng'

# Authentication Backends for social_auth
AUTHENTICATION_BACKENDS = (
    'social_auth.backends.twitter.TwitterBackend',
    'social_auth.backends.facebook.FacebookBackend',
    'social_auth.backends.contrib.github.GithubBackend',
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

SOCIAL_AUTH_FORCE_POST_DISCONNECT = True
# SOCIAL_AUTH_REDIRECT_IS_HTTPS = True
SOCIAL_AUTH_UID_LENGTH = 16
SOCIAL_AUTH_ASSOCIATION_HANDLE_LENGTH = 16
SOCIAL_AUTH_NONCE_SERVER_URL_LENGTH = 16
SOCIAL_AUTH_ASSOCIATION_SERVER_URL_LENGTH = 16
SOCIAL_AUTH_ASSOCIATION_HANDLE_LENGTH = 16

SOCIAL_AUTH_ENABLED_BACKENDS = ('github', 'twitter', 'facebook',)
SOCIAL_AUTH_DEFAULT_USERNAME = 'socialauth_user'
SOCIAL_AUTH_COMPLETE_URL_NAME = 'socialauth_complete'
SOCIAL_AUTH_ASSOCIATE_URL_NAME = 'socialauth_associate_complete'

# Setup needed OAuth keys for social_auth
TWITTER_CONSUMER_KEY = 'YecmHUI9uEPF8gpCHliQ'
TWITTER_CONSUMER_SECRET = 'R9yMWVriMxsoBvhIO6guDiQLEIYXW7wcT2bHimjS7Y'
FACEBOOK_APP_ID = '224844337683823'
FACEBOOK_API_SECRET = 'ecfcf5beadfb0e81061a5aa0d116c207'
GITHUB_APP_ID = '0986cfea7a082b0228e0'
GITHUB_API_SECRET = 'b628aaaa81dc0c32767ad507fb90afaf1b019270'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = ''
LOGIN_ERROR_URL = '/login-error/'
# SOCIAL_AUTH_BACKEND_ERROR_URL = '/query/social_auth_error/'