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

    def _save(self, name, content):
        cleaned_name = self._clean_name(name)
        name = self._normalize_name(cleaned_name)
        parameters = self.object_parameters.copy()
        _type, encoding = mimetypes.guess_type(name)
        content_type = getattr(content, 'content_type', None)
        content_type = content_type or _type or self.default_content_type

        # setting the content_type in the key object is not enough.
        parameters.update({'ContentType': content_type})

        if self.gzip and content_type in self.gzip_content_types:
            content = self._compress_content(content)
            parameters.update({'ContentEncoding': 'gzip'})
        elif encoding:
            # If the content already has a particular encoding, set it
            parameters.update({'ContentEncoding': encoding})

        encoded_name = self._encode_name(name)
        obj = self.bucket.Object(encoded_name)
        logger.log(type(obj))
        logger.log(obj)
        if self.preload_metadata:
            self._entries[encoded_name] = obj

        self._save_content(obj, content, parameters=parameters)
        # Note: In boto3, after a put, last_modified is automatically reloaded
        # the next time it is accessed; no need to specifically reload it.
        return cleaned_name