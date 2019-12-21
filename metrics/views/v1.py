from rest_framework import status
from rest_framework.views import APIView

from artist_portal._helpers import responses
from metrics.serializers.v1 import *


class StreamView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = StreamSerializer(data=request.data, *args, **kwargs)
        if serializer.is_vaild():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_417_EXPECTATION_FAILED)
        
        return responses.DEFAULT_400_RESPONSE

