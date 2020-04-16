from . import base

# -----------------------------------------------------------------------------

class PermissionError(base.ForbiddenError):
    default_detail = "you are not authorized to make this request"

