import logging
from storages.backends.s3boto3 import S3Boto3Storage

logger = logging.getLogger(__name__)

class StaticStorage(S3Boto3Storage):
    location = 'static'
    default_acl = 'public-read'

class MediaStorage(S3Boto3Storage):
    location = 'media'
    default_acl = 'public-read'
    file_overwrite = False

    def _save_content(self, obj, content, parameters):
        logger.log(20, obj)
        logger.log(20, type(obj))
        super()._save_content(obj, content, parameters)