from revibe.settings.base import *

ENV = 'PROD'
DEBUG = False
ADMIN_PATH = '68t9gui2btw4gfesvd89yiugh2354rw/'

ALLOWED_HOSTS = [
    'api.revibe.tech',
    '.revibe.tech',
    '.elasticbeanstalk.com',
    '7623rwqey8ufdshbij.com', # Custom agent to allow for health checks
]

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



# AWS stuff
USE_S3 = True
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

_log_level = 'INFO' 

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'file': {
#             'level': _log_level,
#             'class': 'logging.FileHandler',
#             'filename': '/opt/python/log/django.log',
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['file'],
#             'level': _log_level,
#             'propagate': True,
#         },
#     },
# }

_redis_url = "test-env-redis.7pqvq5.ng.0001.use2.cache.amazonaws.com"
_redis_port = 6379
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(_redis_url, _redis_port)]
        }
    }
}

CELERY_BROKER_URL = "sqs://"
CELERY_BROKER_TRANSPORT_OPTIONS = {
    'region': 'us-east-2',
    'visibility_timeout': 3600,
    # 'polling_interval': 10,
    'queue_name_prefix': f'celery-{ENV}',
    'CELERYD_PREFETCH_MULTIPLIER': 0,
}
