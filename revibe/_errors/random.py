from rest_framework.exceptions import APIException

from revibe._helpers import status

# -----------------------------------------------------------------------------

class PlatformNotFoundError(Exception):
    pass

class ValidationError(Exception):
    pass
