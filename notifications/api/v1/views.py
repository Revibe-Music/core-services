"""
Created: 10 June 2020
"""

from django.http import HttpResponse
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes

from PIL import Image

from notifications.utils.models.notification import mark_email_as_read

# -----------------------------------------------------------------------------

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def email_image_attribution(request, id=None, *args, **kwargs):
    """
    GET request with an ID in the request that links to a notification ID (or other field),
    and will mark that notification as having been opened.
    """

    # mark the email
    mark_email_as_read(id)

    # create an image
    img = Image.new('RGBA', (1, 1))

    return HttpResponse(img, content_type='image/png')


