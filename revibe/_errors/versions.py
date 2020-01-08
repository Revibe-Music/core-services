from rest_framework.exceptions import APIException

from revibe._helpers import status

# -----------------------------------------------------------------------------

class VersionError(APIException):
    status_code = status.HTTP_512_PROGRAM_ERROR
    default_detail = "there was an issue calling the correct API version"
    default_code = 'program error'