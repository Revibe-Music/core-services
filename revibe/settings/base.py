"""
Django settings for revibe project.

Generated by 'django-admin startproject' using Django 2.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

from django.utils.translation import gettext_lazy as _

import os
import sys

from logging import getLogger
logger = getLogger(__name__)

from revibe.environment.network import getHostIP
from revibe import jet
from revibe._helpers import const

# -----------------------------------------------------------------------------

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'kqjvskii-n3exogny_&n7$lm)1w#_^16$a$zhdc7r*&#6(g=sf'
VERSION = '1.1.5'

INSTALLED_APPS = [
    # cors stuff
    'corsheaders',

    # django jet admin portal
    # 'jet.dashboard',
    'jet',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # my apps
    'accounts',
    'accounts.referrals',
    'administration',
    'communication',
    'content',
    'cloud_storage',
    'customer_success.apps.CustomerSuccessConfig',
    'distribution',
    'marketplace',
    'merch',
    'metrics',
    'music',
    'notifications',
    'payments',
    'surveys',

    # installed apps
    'rest_framework',
    'rest_framework.authtoken',     # Need this for allauth social account tokens
    'oauth2_provider',
    'rest_auth',
    # 'knox',
    'storages',

    'channels',
    'django_celery_beat',

    # all auth stuff
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.openid',
    'allauth.socialaccount.providers.spotify',
    'allauth.socialaccount.providers.twitter',
]

MIDDLEWARE = [
    # cors stuff
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',

    # defaults
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    #OAuth Toolkit
    'accounts.middleware.OAuth2TokenOrCookieMiddleware',

    # custom middleware
    # 'revibe.middleware.metrics.RequestMetricsMiddleware',
    # 'revibe.middleware.sessions.MobileAppSessionLoggingMiddleware',
]

AUTH_USER_MODEL = 'accounts.CustomUser'

SITE_ID = 1

ROOT_URLCONF = 'revibe.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'revibe.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
# must be defined in specific settings


REST_FRAMEWORK = {
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'accounts.adapter.TokenAuthSupportQueryString',
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        # 'rest_framework.authentication.SessionAuthentication', # To keep the Browsable API # disabled to remove CSRF checks
        'revibe.authentication.CsrfExemptSessionAuthentication', # https://stackoverflow.com/questions/30871033/django-rest-framework-remove-csrf
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'EXCEPTION_HANDLER': 'revibe._errors.handler.custom_exception_hanlder'
}

### Specify the authentication backends ###
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend', # To keep the Browsable API
    'oauth2_provider.backends.OAuth2Backend',
)

### OAUTH TOOLKIT STUFF ###
OAUTH2_PROVIDER = {
    'SCOPES': {
        'read': 'Read scope',
        'write': 'Write scope',
        'ADMIN': 'override on everything',
        # for first-party applications/users only
        'first-party': 'For users of first-party Revibe applications',
        # account scopes
        'read-user-profile':'Read user data and profile data',
        'write-user-profile': 'Write user data and profile data',
        'write-user-artist': 'Write user and user-artist data',
        'read-user-artist': 'Read user and user-artist data',
        'manager': 'Manage Linked Artists',
        # ...
        # Music scopes
        'write-artists': 'write artists',
        'read-artists': 'Read artists',
        'write-albums': 'Write album data',
        'read-albums': 'Read album data',
        'write-album-contrib': 'Write album contributions',
        'read-album-contrib': 'Read album contributions',
        'write-songs': 'Write song data',
        'read-songs': 'Read song data',
        'write-song-contrib': 'Write song contributions',
        'read-song-contrib': 'Read song contributions',
        'write-library': 'Write library data',
        'read-library': 'Read library data',
        'write-playlist': 'Write playlist data',
        'read-playlist': 'Read playlist data',
        # ...
    },
    'ACCESS_TOKEN_EXPIRE_SECONDS': 3600,  # 2 hours
    'REFRESH_TOKEN_EXPIRE_SECONDS': None,  # Dont expire refresh tokens
    'ROTATE_REFRESH_TOKEN': False,  # Sends a new refresh token when a access token is refreshed.
    'CLIENT_SECRET_GENERATOR_LENGTH': 100,
}

OAUTH2_PROVIDER_APPLICATION_MODEL = 'oauth2_provider.Application'
OAUTH2_PROVIDER_GRANT_MODEL = 'oauth2_provider.Grant'
OAUTH2_PROVIDER_ACCESS_TOKEN_MODEL = 'oauth2_provider.AccessToken'
OAUTH2_PROVIDER_REFRESH_TOKEN_MODEL = 'oauth2_provider.RefreshToken'

SOCIALACCOUNT_QUERY_EMAIL=True
SOCIALACCOUNT_STORE_TOKENS=True

#Social Account Settings
SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        'METHOD': 'oauth2',
        # 'SDK_URL': '//connect.facebook.net/{}/sdk.js', # leave out to use the default
        'SCOPE': ['email', 'public_profile'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'INIT_PARAMS': {'cookie': True},
        'FIELDS': [
            'id',
            'email',
            'first_name',
            'last_name',
        ],
        'EXCHANGE_TOKEN': True,
        'LOCALE_FUNC': lambda request: 'en_US',
        'VERIFIED_EMAIL': False,
        'VERSION': 'v7.0',
    },
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'offline',
        }
    },
    'spotify': {
        'SCOPE': [
            "user-read-private",
            "playlist-read",
            "playlist-read-private",
            'user-library-read',
            'user-library-modify',
            'user-top-read',
            "streaming"
        ],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'EXCHANGE_TOKEN': True,
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/


STATIC_URL = '/static/'

# CORS settings
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

# all_auth settings
ACCOUNT_EMAIL_REQUIRED = False

# admin portal settings
ADMIN_PATH = 'admin/'

# django-jet settings
JET_DEFAULT_THEME = 'default'
JET_THEMES = jet.themes
JET_SIDE_MENU_ITEMS = jet.side_menu

JET_INDEX_DASHBOARD = 'revibe.dashboard.CustomIndexDashboard'

# django channels settings
ASGI_APPLICATION = 'revibe.routing.application'

# celery config
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_BACKEND = None
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE


# logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(messaged)s',
            'datefmt': '%y %b %d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        # 'celery': {
        #     'level': 'DEBUG',
        #     'class': 'logging.handlers.RotatingFileHandler',
        #     'filename': '/opt/python/log/celery.log',
        #     'formatter': 'simple',
        #     'maxBytes': 1024 * 1024 * 100, # 100 mb
        # },
    },
    # 'loggers': 
    # {
    #     'celery': {
    #         'handlers': ['celery', 'console',],
    #         'level': 'INFO',
    #     },
    # },
    # {
    #     'revibe': {
    #         'handlers': ['console',],
    #         'level': 'INFO',
    #     },
    # },
}


AUDIO_FILE_OUTPUT_FORMATS = [
    {
        "format": "mp4",
        "encoding": "aac",
        "bitrate": "96k",
        "filename": "low",
    },
    {
        "format": "mp4",
        "encoding": "aac",
        "bitrate": "128k",
        "filename": "medium",
    },
    {
        "format": "mp4",
        "encoding": "aac",
        "bitrate":"256k",
        "filename": "high",
    },
]

