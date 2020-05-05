"""
Author: Jordan Prechac
Created: 06 Jan, 2020
"""

from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from logging import getLogger
logger = getLogger(__name__)

from revibe._helpers import responses

# -----------------------------------------------------------------------------

@api_view(['GET'])
@permission_classes([AllowAny])
def home(request):
    """
    This is the health-check endpoint. The AWS Elastic Load Balancer (Target
    Group) will check this endpoint for a 200 response to determine application
    health.

    TODO: build this out into a series of checks for application health.
    """
    # check database connection
    # ...
    return responses.OK()

def blank_request(request, *args, **kwargs):
    return HttpResponse(status=200)
