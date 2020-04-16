from . import base

# -----------------------------------------------------------------------------

class VersionError(base.ProgramError):
    default_detail = "there was an issue calling the correct API version"