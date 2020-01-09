from rest_framework.exceptions import APIException

from revibe._helpers import const, status

# -----------------------------------------------------------------------------


class NoAuthenticationError(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "could not identify a user, please try again with proper authentication"
    default_code = "unauthorized"
