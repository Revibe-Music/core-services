"""
"""

from accounts.utils.models import generate_sharing_link
from administration.utils.models import retrieve_variable

# -----------------------------------------------------------------------------

def mobile_app_sharing_link(user):
    base_text = retrieve_variable('mobile_app_share_text', "{}")

    return base_text.format(generate_sharing_link(user))
