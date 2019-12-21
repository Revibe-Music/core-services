from rest_framework import status
from rest_framework.response import Response


def DEFAULT_400_RESPONSE(*args, **kwargs):
    return Response({"detail": "issue processing request, please try again"}, status=status.HTTP_400_BAD_REQUEST)

def NO_REQUEST_TYPE(*args, **kwargs):
    return Response({"detail": "could no identify request type"}, status=status.HTTP_400_BAD_REQUEST)

def SERIALIZER_ERROR_RESPONSE(serializer=None, *args, **kwargs):
    return Response(serializer.errors, status=status.HTTP_417_EXPECTATION_FAILED)

def CREATED(serializer=None, *args, **kwargs):
    response = Response(status=status.HTTP_201_CREATED)
    if serializer:
        response.data = serializer.data
    return response

def UPDATED(serializer=None, *args, **kwargs):
    response = Response(status=status.HTTP_200_OK)
    if serializer:
        response.data = serializer.data
    return response

def DELETED(*args, **kwargs):
    return Response(status=status.HTTP_204_NO_CONTENT)
