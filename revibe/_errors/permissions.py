from rest_framework.exceptions import APIException

from revibe._helpers import const, status

# -----------------------------------------------------------------------------

class PermissionError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "you are not authorized to make this request"
    default_code = "forbidden"

