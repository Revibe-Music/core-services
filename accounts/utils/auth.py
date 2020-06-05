"""
Created: 5 Mar. 2020
Author: Jordan Prechac
"""

from django.db.models.query import QuerySet
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from oauth2_provider.models import Application, AccessToken, RefreshToken
from oauthlib import common

import datetime
import gc
import random
import string

from revibe._errors.accounts import AccountNotFound
from revibe._helpers import const
from revibe.contrib.email import EmailConfiguration
from revibe.utils.params import get_request_header

from accounts.exceptions import PasswordValidationError, AuthError
from accounts.models import CustomUser, Profile
from administration.utils import retrieve_variable

# -----------------------------------------------------------------------------

def generate_scopes(user, application: Application, return_as_string: bool =True):
    scopes = []

    if 'revibe' in application.name.lower():
        scopes.append('first-party')

    if application.name == 'Revibe Music':
        scopes.append('music')

    if application.name == 'Revibe Artists':
        scopes.append('artist')

    if user.is_staff:
        scopes.append('ADMIN')

    if return_as_string:
        return " ".join(scopes)
    else:
        return scopes


def generate_tokens(user: CustomUser, request, use_default_app: bool =False, delete_old_tokens: bool=False, *args, **kwargs):
    """


    Steps:
    1. Get the app header and the corresponding Application
    2. Get the extra info for the tokens
    3. Create an Access Token
    4. Create a Refresh Token
    5. Delete old tokens (conditional)
    """
    # Step 1.
    app_header_name = "HTTP_X_APPNAME" # X-AppName
    app_name = get_request_header(request, app_header_name)
    if app_name == None:
        if use_default_app:
            app_name = "first_party_application"
        else:
            raise AuthError("No application header found")

    app_name = app_name.replace("_", " ").lower()
    application = Application.objects.filter(name__icontains=app_name).first()

    # Step 2.
    app_name = application.name
    app_name_formatted = app_name.replace(" ", "_").upper()
    time = getattr(const, f"{app_name_formatted}_EXPIRY_TIME")
    expire = timezone.now() + datetime.timedelta(hours=time)

    # Step 3.
    access_token = AccessToken(
        user=user,
        expires=expire,
        token=common.generate_token(),
        application=application,
        scope=generate_scopes(user, application)
    )
    access_token.save()

    # Step 4.
    refresh_token = RefreshToken(
        user=user,
        token=common.generate_token(),
        application=application,
        access_token=access_token
    )
    refresh_token.save()

    access_token.source_refresh_token = refresh_token
    access_token.save()

    # Step 5.
    if delete_old_tokens:
        deleting_tokens = AccessToken.objects.filter(user=user, application=application).exclude(token=access_token.token)
        deleting_tokens.delete()

        deleting_tokens = RefreshToken.objects.filter(user=user, application=application).exclude(token=refresh_token.token)
        deleting_tokens.delete()

    return access_token, refresh_token


def refresh_access_token(refresh_token_token):
    """


    Steps:
    1. Get the Refresh Token
    2. Configure new things for the access token
    3. Save fields to the access token
    """
    # step 1.
    try:
        refresh_token = RefreshToken.objects.get(token=refresh_token_token)
    except RefreshToken.DoesNotExist:
        raise AuthError("Cannot find Refresh Token")

    # step 2.
    new_token = common.generate_token()
    time = getattr(const, f"{refresh_token.application.name.replace(' ','_').upper()}_EXPIRY_TIME")
    expire = timezone.now() + datetime.timedelta(hours=time)

    # step 3.
    access_token = refresh_token.access_token
    access_token.token = new_token
    access_token.expires = expire
    access_token.save()

    return access_token



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
    user.force_change_password = False
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


def reset_password(email=None, username=None, user=None):
    """
    """
    if user:
        if isinstance(user, QuerySet):
            user = user.first()
    else:
        # get the user by email/username
        user = get_user_by_username_or_email(email, username)
    if user == None:
        raise AccountNotFound("Could not find this user")

    # generate temp password
    password_length = retrieve_variable('temporary-password-length', 20, output_type=int)
    letters = string.ascii_letters + string.digits
    temp_password = ''.join(random.choice(letters) for i in range(password_length))

    # set temp password
    user.set_password(temp_password)
    user.force_change_password = True
    user.save()

    # send email with temp password
    email = EmailConfiguration(user, [user.profile.email,], 'reset_password', temp_password=temp_password)
    email.send_email()

    return user.profile.email



