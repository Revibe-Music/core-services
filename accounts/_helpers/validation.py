from logging import getLogger
logger = getLogger(__name__)

from accounts.models import CustomUser, Profile

# -----------------------------------------------------------------------------

def check_username(username):
    try:
        user = CustomUser.objects.get(username=username)
    except CustomUser.DoesNotExist:
        return True
    else:
        logger.warn(f"Username {username} already exists")
        return False

def check_email(email):
    """
    Checks if there is/are user(s) with this email addrees.

    Effectively makes email unique, if enforced wherever email could be updated.
    """
    users = Profile.objects.filter(email=email)
    if len(users) > 0:
        logger.warn(f"User with email '{email}' already exists.")
        return False
    return True
