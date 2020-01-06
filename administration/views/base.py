from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from logging import getLogger
logger = getLogger(__name__)

from revibe._helpers import responses

# -----------------------------------------------------------------------------

@api_view(['GET'])
@permission_classes([AllowAny])
def home(request):
    return responses.OK()
