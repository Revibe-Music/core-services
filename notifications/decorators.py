"""
Created: 08 May 2020
Author: Jordan Prechac
"""

from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest
from rest_framework.request import Request

from functools import wraps

from accounts.models import CustomUser

from .tasks import send_notification

# -----------------------------------------------------------------------------


def notifier(trigger, user_after_request=False, *args, **kwargs):
    """ Sends a notification to the user referenced """

    def decorator(func):

        @wraps(func)
        def wrapper(*func_args, **func_kwargs):
            result = func(*func_args, **func_kwargs)
            
            if not user_after_request:
                def get_user_from_request(request):
                    user = getattr(request, 'user', None)
                    if (user not in [None, ""]) and (not isinstance(user, AnonymousUser)):
                        # we have a user
                        return user
                    return None

                USER = None
                # check the kwargs for a request
                if 'request' in func_kwargs.keys():
                    request = kwargs.get('request')
                    user = get_user_from_request(request)
                    if user != None:
                        USER = user
                # check the args for a request
                if USER == None:
                    for arg in func_args:
                        if isinstance(arg, (HttpRequest, Request)):
                            # the argument is a request
                            user = get_user_from_request(arg)
                            if user != None:
                                USER = user
                                break

                if USER != None:
                    # we found a user in a request somewhere
                    user_id = USER.id
                    send_notification.delay(user_id, trigger, *args, **kwargs)

            # there won't be a user in the request, so we need to look after it
            elif isinstance(result, tuple):
                expect_user = result[1]
                result = result[0]
                if isinstance(expect_user, CustomUser):
                    user_id = expect_user.id
                    send_notification(user_id, trigger, *args, **kwargs)
                    send_notification.delay(user_id, trigger, *args, **kwargs)

            return result

        return wrapper

    return decorator


