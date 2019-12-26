from django.conf import settings
from rest_framework.views import APIView

from artist_portal._helpers import responses
from metrics.serializers.v1 import *


class StreamView(APIView):
    def post(self, request, *args, **kwargs):
        # return an error when not running in the cloud
        if not settings.USE_S3:
            return responses.BAD_ENVIRONMENT()

        serializer = StreamSerializer(data=request.data, *args, **kwargs)
        if serializer.is_valid():
            serializer.save()
            return responses.CREATED()
        else:
            return responses.SERIALIZER_ERROR_RESPONSE(serializer=serializer)
        
        return responses.DEFAULT_400_RESPONSE()

