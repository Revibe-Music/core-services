"""
Created: 06 May 2020
Author: Jordan Prechac
"""

from rest_framework.exceptions import APIException

from revibe._helpers import status

# -----------------------------------------------------------------------------

# 2xx Errors

class AlreadyReportedError(APIException):
    status_code = status.HTTP_208_ALREADY_REPORTED
    default_detail = "The requested function has already been performed"
    default_code = "already_reported"


# 4xx Errors
class BadRequestError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Bad request"
    default_code = 'bad_request'


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
    default_detail = "Could not find the specified resource"
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

class ServerError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Server error"
    default_code = "server_error"

class NotImplementedError(APIException):
    status_code = status.HTTP_501_NOT_IMPLEMENTED
    default_detail = "The requested feature is not currently available"
    default_code = "not_implemented"

# class BadEnvironmentError(APIException):
class ServiceUnavailableError(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "The requested resource is not available in the current environemnt"
    default_code = "bad_environment"
BadEnvironmentError = ServiceUnavailableError # support older code - changed 16 Apr. 2020

class ProgramError(APIException):
    status_code = status.HTTP_512_PROGRAM_ERROR
    default_detail = "Server error, please try again later"
    default_code = 'program_error'

class PageUnavailableError(APIException):
    status_code = status.HTTP_513_PAGE_UNAVAILABLE
    default_detail = "Page is unavailable"
    default_code = "page_unavailable"

