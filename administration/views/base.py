from rest_framework.decorators import api_view

from logging import getLogger
logger = getLogger(__name__)

from revibe._helpers import responses

# -----------------------------------------------------------------------------

@api_view(['GET'])
def home(request):
    return responses.OK()
