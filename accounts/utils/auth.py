"""
Created: 5 Mar. 2020
Author: Jordan Prechac
"""

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

from revibe._errors.accounts import AccountNotFound

import gc

from accounts.exceptions import PasswordValidationError
from accounts.models import CustomUser

# -----------------------------------------------------------------------------

def change_password(user, old_password, new_password, confirm_new_password):
    """
    """
    # reauthenticate the user to validate the old_password
    user_check = authenticate(username=str(user.username), password=old_password)
    if user_check == None or user_check != user:
        raise AccountNotFound("Could not validate the old password")

    del user_check
    gc.collect()

    # ensure that the new passwords match
    if new_password != confirm_new_password:
        raise PasswordValidationError(f"Passwords do not match")

    # set the new password
    user.set_password(new_password)
    user.save()

