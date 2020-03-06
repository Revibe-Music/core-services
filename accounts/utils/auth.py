"""
Created: 5 Mar. 2020
Author: Jordan Prechac
"""

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

import gc
import random
import string

from revibe._errors.accounts import AccountNotFound
from revibe.contrib.email import EmailConfiguration

from accounts.exceptions import PasswordValidationError
from accounts.models import CustomUser, Profile

# -----------------------------------------------------------------------------

def change_password(user, old_password, new_password, confirm_new_password):
    """
    """
    # reauthenticate the user to validate the old_password
    user_check = authenticate(username=str(user.username), password=old_password)
    if user_check == None or user_check != user:
        raise AccountNotFound("Old password is not correct")

    del user_check
    gc.collect()

    # ensure that the new passwords match
    if new_password != confirm_new_password:
        raise PasswordValidationError("Passwords do not match")

    # set the new password
    user.set_password(new_password)
    user.save()


def get_user_by_username_or_email(email=None, username=None):
    """
    """
    if username != None:
        user = CustomUser.objects.get(username=username)
        return user

    elif email != None:
        profile = Profile.objects.get(email=email)
        return profile.user
    
    return None


def reset_password(email=None, username=None):
    """
    """
    # get the user by email/username
    user = get_user_by_username_or_email(email, username)
    if user == None:
        raise AccountNotFound("Could not find this user")

    # generate temp password
    letters = string.ascii_letters + string.digits
    temp_password = ''.join(random.choice(letters) for i in range(20))

    # set temp password
    user.set_password(temp_password)
    user.force_change_password = True
    user.save()

    # send email with temp password
    email = EmailConfiguration(user, [user.profile.email,], 'forgot_password', temp_password=temp_password)
    email.send_email()

