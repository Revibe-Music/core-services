from rest_framework.status import *
from rest_framework.response import Response

# from artist_portal._helpers import const # may need later


# 1xx responses


# 2xx responses

def OK(serializer=None, detail=None, *args, **kwargs):
    response = Response(status=HTTP_200_OK)
    if serializer:
        response.data = serializer.data
    elif detail:
        response.data = {"detail": detail}
    return response

def UPDATED(serializer=None, *args, **kwargs):
    response = Response(status=HTTP_200_OK)
    if serializer:
        response.data = serializer.data
    return response

def CREATED(serializer=None, *args, **kwargs):
    response = Response(status=HTTP_201_CREATED)
    if serializer:
        response.data = serializer.data
    return response

def DELETED(*args, **kwargs):
    return Response(status=HTTP_204_NO_CONTENT)


# 3xx responses


# 4xx responses

def DEFAULT_400_RESPONSE(*args, **kwargs):
    return Response({"detail": "issue processing request, please try again"}, status=HTTP_400_BAD_REQUEST)

def NO_REQUEST_TYPE(*args, **kwargs):
    return Response({"detail": "could no identify request type"}, status=HTTP_400_BAD_REQUEST)

def UNAUTHORIZED(detail=None, *args, **kwargs):
    response = Response(status=HTTP_401_UNAUTHORIZED)
    detail = detail if detail else "could not identify the current user"
    response.data = {"detail": detail}
    return response

def PAYMENT_REQUIRED(detail=None, *args, **kwargs):
    response = Response(status=HTTP_402_PAYMENT_REQUIRED)
    detail = detail if detail else "cannot access this feature without paid services"
    response.data = {"detail": detail}
    return Response

def NOT_PERMITTED(detail=None, *args, **kwargs):
    response = Response(status=HTTP_403_FORBIDDEN)
    response.data = {"detail": detail} if detail else {"detail": "you are not authorized to make this request"}
    return response

def CONFLICT(detail=None, *args, **kwargs):
    response = Response(status=HTTP_409_CONFLICT)
    detail = detail if detail else "instance already exists"
    response.data = {"detail": detail}
    return response

def UNSUPPORTED_MEDIA_TYPE(detail=None, *args, **kwargs):
    response = Response(status=HTTP_415_UNSUPPORTED_MEDIA_TYPE)
    detail = detail if detail else "cannot accept this media type/format"
    response.data = {"detail": detail}
    return response

def SERIALIZER_ERROR_RESPONSE(serializer=None, detail=None, *args, **kwargs):
    response = Response(status=HTTP_417_EXPECTATION_FAILED)
    if serializer:
        response.data = serializer.errors
    elif detail:
        response.data = {"detail": detail}
    return response


# 5xx responses

def NOT_IMPLEMENTED(detail=None, *args, **kwargs):
    response = Response(status=HTTP_501_NOT_IMPLEMENTED)
    if not detail:
        detail = "this functionality has not yet been built"
    response.data = {"detail": detail}
    return response

def BAD_ENVIRONMENT(detail=None, *args, **kwargs):
    response = Response(status=HTTP_503_SERVICE_UNAVAILABLE)
    detail = detail if detail else "this functionality is only accessible in a cloud environment"
    response.data = {"detail": detail}
    return response

