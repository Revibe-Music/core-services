from rest_framework import status
from rest_framework.response import Response

DEFAULT_400_RESPONSE = Response({"detail": "issue processing request, please try again"}, status=status.HTTP_400_BAD_REQUEST)

NO_REQUEST_TYPE = Response({"detail": "could no identify request type"}, status=status.HTTP_400_BAD_REQUEST)

def SERIALIZER_ERROR_RESPONSE(serializer=None):
    return Response(serializer.errors, status=status.HTTP_417_EXPECTATION_FAILED)

def CREATED(serializer=None):
    response = Response(status=status.HTTP_201_CREATED)
    if serializer:
        response.data = serializer.data
    return response

def UPDATED(serializer=None):
    response = Response(status=status.HTTP_200_OK)
    if serializer:
        response.data = serializer.data
    return response
