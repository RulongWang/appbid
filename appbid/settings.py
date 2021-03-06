# coding: utf-8
# Django settings for appbid project.
#!/usr/bin/python
import os
import datetime

DEBUG = True
TEMPLATE_DEBUG = False

ADMINS = (
    ('AppsWalk', 'support@appswalk.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'appbid',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '127.0.0.1',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '3306',                      # Set to empty string for default.
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = '*'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Asia/Shanghai'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'
LANGUAGES = (
    ('zh-cn', u'简体中文'),
    ('en-us', u'English'),
)
LOCALE_PATHS = (
    os.path.join(os.path.dirname(__file__), '..', 'locale').replace('\\', '/'),
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False #TODO:Need check if the time is correct,when deploy project.

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), '..', '..', 'attachment').replace('\\', '/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(os.path.dirname(__file__), '..', 'static').replace('\\', '/'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '@$wu5b+#eoh&h3p3s2oh8&q3ja+x$sorrx@2(g6qp0k%g2w83a'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'social_auth.context_processors.social_auth_by_type_backends',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
)

ROOT_URLCONF = 'appbid.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'appbid.wsgi.application'

TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), '..', 'templates').replace('\\', '/'),)

INSTALLED_APPS = (

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    #'django_ses',
    'django.contrib.flatpages',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'django.contrib.comments',
    'django_crontab',
    'social_auth',
    'qrcode',
    'requests',
    'twython',
    #The package list
    'appbid',
    'bid',
    'home',
    'message',
    'notification',
    'order',
    'payment',
    'system',
    'seller',
    'usersetting',
    'credit',
    'dashboard',
    'transaction',
    'paypal',
    'auth',
    'favicon',
    'job',
    'offer',
)

try:
    from auth.settings import *
except Exception, e:
    pass

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING_ROOT = os.path.join(os.path.dirname(__file__), '..', '..', 'logs/').replace('\\', '/')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'standard': {
            'format': '[%(asctime)s][%(threadName)s:%(thread)d][%(levelname)s][%(pathname)s/%(filename)s:%(lineno)d-%(funcName)s] - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
        # 'file': {
        #     'level': 'INFO',
        #     'class': 'logging.handlers.RotatingFileHandler',
        #     'filename': ''.join([LOGGING_ROOT, 'app.log.']),
        #     'maxBytes': 1024*1024*5,
        #     'backupCount': 5,
        #     'formatter': 'standard'
        # },
        'default': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': ''.join([LOGGING_ROOT, 'appbid.log.', datetime.datetime.now().strftime('%Y-%m-%d')]),#%Y-%m-%d-%H-%M
            'when': 'midnight',#S M H D W midnight
            'interval': 1,
            'backupCount': 5,
            'formatter': 'standard',
        },
        'email': {
            'level': 'ERROR',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': ''.join([LOGGING_ROOT, 'email.log.', datetime.datetime.now().strftime('%Y-%m-%d')]),#%Y-%m-%d-%H-%M
            'when': 'midnight',#S M H D W midnight
            'interval': 1,
            'backupCount': 5,
            'formatter': 'standard',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'appbid': {
            'handlers': ['default', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'email': {
            'handlers': ['default', 'email', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django_crontab': {
            'handlers': ['default', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}

FILE_CHARSET = 'utf-8'

DEFAULT_CHARSET = 'utf-8'

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

#Set email config
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'#Send the mail actually
#EMAIL_BACKEND = 'django_smtp_ssl.SSLEmailBackend'
#EMAIL_BACKEND = 'django_ses.SESBackend'
#AWS_ACCESS_KEY_ID = 'AKIAIZOLHXT23DTCJ7LQ'
#AWS_SECRET_ACCESS_KEY = 'AoW+7BtPEXWG1RQRnPAfpupateV4r0YEV42ggANfG7mU'
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'#Show by console
EMAIL_USE_TLS = True
#EMAIL_HOST = 'email-smtp.us-east-1.amazonaws.com'
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_PORT = 587 #465
#EMAIL_HOST_USER = 'AKIAIZOLHXT23DTCJ7LQ'#your email username
EMAIL_HOST_USER = 'postmaster@webmaster.appswalk.com'#your email username
#EMAIL_HOST_PASSWORD = 'AoW+7BtPEXWG1RQRnPAfpupateV4r0YEV42ggANfG7mU' #your email passowrdEMAIL_HOST_USER = 'AKIAIZOLHXT23DTCJ7LQ'#your email username
EMAIL_HOST_PASSWORD = '2yt7pu-k8jn3' #your email passowrd
EMAIL_SENDER = 'support@appswalk.com'

CRONJOBS = [
    #Run every night at midnight
    ('1 0 * * *', 'job.job.jobByMidnight'),
    #Run every four hour
    ('0 */4 * * *', 'job.job.jobByFourHour'),
    #Run every hour
    ('0 */1 * * *', 'job.job.jobByEveryHour'),
    #Run every five min
    ('*/5 * * * *', 'job.job.jobByFiveMin'),
]

try:
    from paypal.settings import *
except Exception, e:
    pass

#flat page setting
SITE_ID = 1

FAVICON_PATH = STATIC_URL + 'images/favicon.ico'
