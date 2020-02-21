"""
Created: 21 Feb. 2020
Author: Jordan Prechac

Functions that make it easy to operate with objects in S3
"""

from django.conf import settings

import boto3

# -----------------------------------------------------------------------------

def delete_s3_object(file, *args, **kwargs):
    """
    Deletes an object from the S3 bucket
    """
    if not getattr(settings, 'USE_S3', False):
        return None
    # get the string thing
    s3_string = f"media/{file.name}"

    # get s3
    s3 = boto3.resource('s3')
    s3.Object(settings.AWS_STORAGE_BUCKET_NAME, s3_string).delete()

