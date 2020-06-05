"""
Created: 16 Mar. 2020
Author: Jordan Prechac
"""

from django.conf import settings
from django.db import IntegrityError
from django.utils import timezone
from oauth2_provider.models import Application, AccessToken, RefreshToken
from oauthlib import common

import datetime

from revibe.utils import mailchimp
from revibe.utils.params import get_url_param
from revibe.utils.urls import add_query_params
from revibe._errors import network
from revibe._helpers import const

from accounts._helpers import validation
from accounts.models import CustomUser
from accounts.referrals.tasks import add_referral_points
from accounts.referrals.utils import attach_referral as attach_user_referral
from accounts.serializers import v1 as act_ser_v1
from accounts.utils.auth import generate_tokens
from administration.utils.models import retrieve_variable
from administration.models import Campaign

from .tokens import delete_old_tokens

# -----------------------------------------------------------------------------

def generate_sharing_link(user):
    """
    """
    base_url = retrieve_variable('mobile_app_share_link', "https://apps.apple.com/us/app/revibe-music/id1500839967")
    params = {"uid": str(user.id)}
    final_url = add_query_params(base_url, params)

    return final_url


def attach_referrer(params, profile, *args, **kwargs):
    """
    Looks in the params for a user or campaign referral and attaches it to the profile.
    """
    # check for marketing campaign
    cid = get_url_param(params, 'cid')
    if cid != None:
        try:
            campaign = Campaign.objects.get(uri=cid)
            profile.campaign = campaign
            profile.save()
        except Exception as e:
            pass

    # check for user referral
    uid = get_url_param(params, 'uid')
    if uid != None:
    #     try:
    #         referrer = CustomUser.objects.get(id=uid)
    #         profile.referrer = referrer
    #         profile.save()
    #     except Exception as e:
    #         pass
        try:
            referrer = CustomUser.objects.get(id=uid)
            referree = profile.user
            attach_user_referral(
                referrer=referrer,
                referree=referree,
                ip_address=kwargs.get('ip_address', None)
            )
        except Exception as e:
            print(e)

    return profile


def validate_username_and_email(username, email):
    errors = {}
    useranme_errors = []
    email_errors = []

    # username validation
    if not username:
        username_errors.append("Field 'username' is required")
    if not validation.check_username(username):
        useranme_errors.append(f"Username '{username}' already exists")
    # add any errors to the errors dict
    if useranme_errors != []:
        errors['username'] = useranme_errors

    # email validation
    if email and (not validation.check_email(email)):
        email_errors.append(f"Email '{email}' is already in use")
    # add any errors to the errors dict
    if email_errors != []:
        errors['email'] = email_errors
    
    # raise an error if there are errors
    if errors != {}:
        raise network.ConflictError(detail=errors)


def register_new_user(data, params, old_user=None, *args, **kwargs):
    """
    """
    # check if this is a temporary account upgrade
    if old_user:
        data = create_permanent_account(old_user, data, *args, **kwargs)
        return data
    
    # check for username and email
    username = data.get('username', None)
    email = data.get('email', None)
    # validate username and email
    validate_username_and_email(username, email)

    # perform the save
    serializer = act_ser_v1.UserSerializer(data=data)
    if not serializer.is_valid():
        raise network.BadRequestError(detail=serializer.errors)
    try:
        user = serializer.save()
    except IntegrityError as err:
        raise network.ProgramError(detail=str(err))
    
    device = data['device_type']
    application = Application.objects.get(name="Revibe First Party Application")


    # check query params for referral info
    attach_referrer(params, user.profile)

    # additional checks and stuff
    if not user.temporary_account:
        user.date_registered = timezone.now()

    # get the tokens set up
    access_token, refresh_token = generate_tokens(user, kwargs.get('request'), use_default_app=True)

    # prep return information
    data = {
        "user": user,
        "access_token": access_token,
    }

    if device != 'browser':
        data.update({"refresh_token": refresh_token})
    
    if not settings.DEBUG:
        try:
            mailchimp.add_new_list_member(user)
        except Exception:
            pass
    
    # assign points for referral stuff
    try:
        add_referral_points.s(user.id, "new_user", datetime.datetime.now()).delay()
    except Exception:
        pass

    return data


def create_permanent_account(user, data, *args, **kwargs):
    """
    This can only happen from the mobile app
    """
    # raise exception if this is not a temp account
    if user.temporary_account == False:
        raise network.ForbiddenError("This account cannot be claimed")

    # validate request data
    if 'username' not in data.keys():
        raise network.BadRequestError("Field 'username' is required")
    if 'password' not in data.keys():
        raise network.BadRequestError("Field 'password' is required")

    application = Application.objects.get(name="Revibe First Party Application")

    # reset user's information
    username = data.get("username")
    password = data.get("password")

    user.username = username
    user.set_password(password)
    user.force_change_password = False
    user.temporary_account = False
    user.date_registered = timezone.now()
    user.save()

    # generate new tokens
    delete_old_tokens(user)

    time = const.DEFAULT_EXPIRY_TIME
    expire = timezone.now() + datetime.timedelta(hours=time)

    scopes = ['first-party']
    scope = " ".join(scopes)

    access_token = AccessToken.objects.create(
        user=user,
        expires=expire,
        token=common.generate_token(),
        application=application,
        scope=scope
    )
    refresh_token = RefreshToken.objects.create(
        user=user,
        token=common.generate_token(),
        application=application,
        access_token=access_token
    )
    access_token.source_refresh_token = refresh_token
    access_token.save()

    return {
        "user": user,
        "access_token": access_token
    }

