from . import base
from revibe._helpers import const, status

# -----------------------------------------------------------------------------

class ParameterMissingError(base.ExpectationFailedError):
    default_detail = "missing paramter, please check the docs for request requirements"


class SerializerValidationError(base.ExpectationFailedError):
    default_detail = "misc. serializer error, please try again"


class TooManyObjectsReturnedError(base.ProgramError):
    default_detail = "Too many objects found, please try again"


class ObjectAlreadyExists(base.AlreadyReportedError):
    default_detail = "The request object already exists"


class NoKeysError(base.ServiceUnavailableError):
    default_detail = "Could not find any valid keys"
