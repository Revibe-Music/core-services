from rest_framework.exceptions import APIException

from revibe._errors import network
from revibe._helpers import status

# -----------------------------------------------------------------------------

class AccountError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "The request could not be completed, please try again"
    default_code = 'conflict'


class AccountNotFound(network.UnauthorizedError):
    default_detail = "Could not identify the current user, please try again"


class NotArtistError(network.ForbiddenError):
    default_detail = "Could not identify the current artist"

class ProfileNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "The user's profile information could not be found"
    default_code = "not_found"
