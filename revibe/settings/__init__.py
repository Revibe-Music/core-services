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

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False if (os.getenv('DEBUG')=='FALSE') else True

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'api.revibe.tech',
    '.revibe.tech',
    '.revibe.com',
    # '.compute-1.amazonaws.com', # allows viewing of instances directly
    '.elasticbeanstalk.com',
    '7623rwqey8ufdshbij.com', # Custom agent to allow for health checks
]
if (not DEBUG) and ('USE_S3' in os.environ):
    ALLOWED_HOSTS.append(getHostIP())
    logger.info("Added host IP address to ALLOWED_HOSTS")


# Application definition

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
    'administration',
    'communication',
    'content',
    'cloud_storage',
    'distribution',
    'marketplace',
    'merch',
    'metrics',
    'music',
    'notifications',
    'payments',

    # installed apps
    'rest_framework',
    'rest_framework.authtoken',     # Need this for allauth social account tokens
    'oauth2_provider',
    'rest_auth',
    # 'knox',
    'storages',

    'channels',

    # all auth stuff
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.openid',
    'allauth.socialaccount.providers.spotify',
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

if 'RDS_DB_NAME' in os.environ:
    if DEBUG == True: # test environment
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': os.environ['RDS_DB_NAME'],
                'USER': os.environ['RDS_USERNAME'],
                'PASSWORD': os.environ['RDS_PASSWORD'],
                'HOST': os.environ['RDS_HOSTNAME'],
                'PORT': os.environ['RDS_PORT'],
                'OPTIONS': {
                    'charset': 'utf8mb4'
                }
            }
        }
    else: # production environment
        DATABASE_ROUTERS = ['revibe.router.ProductionRouter', ]
        DATABASES = {
            # The production environment defines 2 databases, 'default' and 'read'.
            # 
            # The 'default' database is the Aurora Write database instance, it just
            # can't be called 'write' because Django is stupid.
            # 
            # The 'read' database sets up the cluster endpoint for all the Reader databases,
            # Aurora will automatically balance the load across all read-replicas so we don't
            # have to. In the future, probably around when it becomes worthwhile to have a second
            # read-replica, we should remove the 'default' database as a read option in the
            # router.
            # (written 07 Jan, 2020)
            const.WRITE_DATABASE_NAME: { # write
                'ENGINE': 'django.db.backends.mysql',
                'NAME': os.environ['RDS_DB_NAME'],
                'USER': os.environ['RDS_USERNAME'],
                'PASSWORD': os.environ['RDS_PASSWORD'],
                'HOST': os.environ['RDS_WRITE_HOSTNAME'],
                'PORT': os.environ['RDS_PORT'],
                'OPTIONS': {
                    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                    'charset': 'utf8mb4',
                },
            },
            const.READ_DATABASE_NAME: { # read
                'ENGINE': 'django.db.backends.mysql',
                'NAME': os.environ['RDS_DB_NAME'],
                'USER': os.environ['RDS_USERNAME'],
                'PASSWORD': os.environ['RDS_PASSWORD'],
                'HOST': os.environ['RDS_READ_HOSTNAME'],
                'PORT': os.environ['RDS_PORT'],
                'OPTIONS': {
                    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                    'charset': 'utf8mb4',
                },
            }
        }
else: # local environment
    DATABASES = {
        'default': {
            # 'ENGINE': 'django.db.backends.sqlite3',
            # 'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
            'ENGINE':'django.db.backends.mysql',
            'HOST':'127.0.0.1',
            'PORT':'3306',
            'NAME':'revibe',
            'USER':'django',
            'PASSWORD':'django',
            'OPTIONS': {
                'charset': 'utf8mb4'
            }
        }
    }


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


USE_S3 = os.getenv('USE_S3') == 'TRUE'
if USE_S3:
    # AWS stuff
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = 'us-east-2'
    AWS_DEFAULT_ACL = None
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
    AWS_QUERYSTRING_AUTH = False

    # # static files
    STATIC_LOCATION = 'static'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{STATIC_LOCATION}/'
    STATICFILES_STORAGE = 'revibe.storage_backends.StaticStorage'

    # media file settings
    MEDIA_LOCATION = 'media'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{MEDIA_LOCATION}/'
    DEFAULT_FILE_STORAGE = 'revibe.storage_backends.MediaStorage' # custom storage settings
    # DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage' # default storage settings

    # email settings
    EMAIL_BACKEND = "django_ses.SESBackend"
    AWS_SES_REGION_NAME = "us-east-1"
    AWS_SES_REGION_ENDPOINT = f'email.{AWS_SES_REGION_NAME}.amazonaws.com'

    _log_level = 'DEBUG' if DEBUG else 'INFO' 

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'file': {
                'level': _log_level,
                'class': 'logging.FileHandler',
                'filename': '/opt/python/log/django.log',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['file'],
                'level': _log_level,
                'propagate': True,
            },
        },
    }
else:
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    AWS_ACCESS_KEY_ID = None
    AWS_SECRET_ACCESS_KEY = None

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': 'INFO',
            },
        },
    }

STATIC_URL = '/static/'

# CORS settings
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

# all_auth settings
ACCOUNT_EMAIL_REQUIRED = False

# admin portal settings
ADMIN_PATH = 'admin/' if DEBUG else '68t9gui2btw4gfesvd89yiugh2354rw/'

# django-jet settings
JET_DEFAULT_THEME = 'default'
JET_THEMES = jet.themes
JET_SIDE_MENU_ITEMS = jet.side_menu

JET_INDEX_DASHBOARD = 'revibe.dashboard.CustomIndexDashboard'

# django channels settings
ASGI_APPLICATION = 'revibe.routing.application'
# channel layers
if USE_S3:#DEBUG == True: # local and dev environments
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer"
        }
    }
else: # production environment
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [("api-communication-redis.7pqvq5.ng.0001.use2.cache.amazonaws.com", 6379)]
            }
        }
    }

# celery config
CELERY_BROKER_URL = 'redis://api-communication-redis.7pqvq5.ng.0001.use2.cache.amazonaws.com:6379' if not DEBUG else 'redis://127.0.0.1:6379'
CELERY_RESULT_BACKEND = CELERY_BROKER_URL

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
