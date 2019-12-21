from rest_framework import status
from rest_framework.response import Response

DEFAULT_400_RESPONSE = Response({"detail": "Issue processing request, please try again"}, status=status.HTTP_400_BAD_REQUEST)
