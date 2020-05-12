from revibe.settings.base import *

ENV = 'DEV'
DEBUG = True

ALLOWED_HOSTS = []

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

USE_S3=False

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

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

_redis_url = '127.0.0.1'
_redis_port = 6379
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}
CELERY_BROKER_URL = f"redis://{_redis_url}:{_redis_port}"
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
