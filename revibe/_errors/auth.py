from . import base
from revibe._helpers import const, status

# -----------------------------------------------------------------------------


class NoAuthenticationError(base.UnauthorizedError):
    default_detail = "could not identify a user, please try again with proper authentication"
