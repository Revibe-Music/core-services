from rest_framework.exceptions import APIException

from revibe._helpers import status

# -----------------------------------------------------------------------------

# 4xx Errors
class BadRequestError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Bad request"
    default_code = 'bad_requests'


class UnauthorizedError(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Could not identify a user, please re-authenticate and try again"
    default_code = 'unauthorized'


class ForbiddenError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "You are not permitted to perform the current action"
    default_code = "forbidden"


class NotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Could not find the specified resource, please try again"
    default_code = 'not_found'


class ConflictError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "The request cannot be completed because of a data conflic, please try again"
    default_code = 'conflict'

class ExpectationFailedError(APIException):
    status_code = status.HTTP_417_EXPECTATION_FAILED
    default_detail = "Missing data, please check the docs and try again"
    default_code = "expectation_failed"

# ...

# 5xx Errors

class NotImplementedError(APIException):
    status_code = status.HTTP_501_NOT_IMPLEMENTED
    default_detail = "The requested feature is not currently available"
    default_code = "not_implemented"

class BadEnvironmentError(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "The requested resource is not available in the current environemnt"
    default_code = "bad_environment"

class ProgramError(APIException):
    status_code = status.HTTP_512_PROGRAM_ERROR
    default_detail = "Server error, please try again later"
    default_code = 'program_error'
