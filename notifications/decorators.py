"""
Created: 08 May 2020
Author: Jordan Prechac
"""

from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest
from rest_framework.request import Request

import functools

from accounts.models import CustomUser

from .exceptions import NotificationException
from .tasks import send_notification
from .utils.objects import get_album_id, get_song_id, take_step

# -----------------------------------------------------------------------------
one_hour = 60*60

# def notifier(trigger, user_after_request=False, album=False, song=False, countdown=1, expires=one_hour, *args, **kwargs):
#     """ Sends a notification to the user referenced """

#     def decorator(func):

#         @wraps(func)
#         def wrapper(*func_args, **func_kwargs):
#             result = func(*func_args, **func_kwargs)

#             USER = None
#             REQUEST = get_request(func_args, func_kwargs)

#             # check the request method
#             methods = kwargs.pop('methods', [])
#             if (REQUEST != None) and (methods != []):
#                 methods = [m.upper() for m in methods]
#                 # if the request method is not a notification method, skip all the other stuff
#                 if REQUEST.method not in methods:
#                     return result if not isinstance(result, tuple) else result[0]

#             # check for extra stuff to pass to the Notifier class
#             if album:
#                 kwargs['album_id'] = get_album_id(result)
#             if song:
#                 kwargs['song_id'] = get_song_id(result)

#             # do the normal check for a request
#             if not user_after_request:
#                 if REQUEST != None:
#                     USER = get_user_from_request(REQUEST)

#             # there won't be a user in the request, so we need to look after it
#             elif (USER == None) and isinstance(result, tuple):
#                 expect_user = result[1]
#                 result = result[0]
#                 if isinstance(expect_user, CustomUser):
#                     USER = expect_user


#             # we found a user in a request somewhere
#             if USER != None:
#                 user_id = USER.id
#                 # send_notification.delay(user_id, trigger, *args, **kwargs)
#                 send_notification.s(user_id, trigger, *args, **kwargs) \
#                     .set(countdown=countdown) \
#                     .set(expires=expires) \
#                     .delay()

#             return result

#         return wrapper

#     return decorator

class NotifierDecorator:
    """
    Decorator for sending notifications for defined actions.

    Args:
        trigger (str): Action that triggers the firing of a notification.
            Will be used as a lookup in the Event objects.
        methods (list, optional): List of allowed methods.
            Defaults to [], representing any method.
        user_after_request (bool): Check the result of the function for a user,
            instead of the args & kwargs of the function.
            Defaults False
        album (bool): An album object will be returned, so attach it's ID to the Notifier class.
            Defaults to False
        song (bool): See `album`, but with a song object.
            Defaults to False
        countdown (int): Seconds to wait until the function is triggered in Celery
            Defaults to 1
        expires (int, datetime.datetime): Seconds until the function is expired,
            or the time in which the function should expire.
            Defaults to 3600 (one hour)
        *conf_args: Variable length argument list.
        **conf_kwargs: Arbitrary keyword arguments.
    """
    # set of attributes needed for DRF's @action decorator
    mapping = None
    detail = None
    url_path = None
    url_name = None
    kwargs = None

    def __init__(self, trigger, user_target=None, methods=[], user_after_request=False, album=False, song=False, countdown=1, expires=one_hour, *conf_args, **conf_kwargs):
        self.trigger = trigger
        self.user_after_request = user_after_request
        self.album = album
        self.song = song
        self.countdown = countdown
        self.expires = expires
        self.conf_args = conf_args
        self.conf_kwargs = conf_kwargs
        self.methods = [m.upper() for m in methods]

        self.user = None
        self.request = None

        if user_target != None:
            self.inverse = True
            self.user_target = user_target
        else:
            self.inverse = False
        

    def __call__(self, func):
        # set docstrings and names
        # self.__doc__ = func.__doc__
        # self.__name__ = func.__name__
        def wrapper(*func_args, **func_kwargs):
            try:
                result = func(*func_args, **func_kwargs)
            except Exception as e:
                raise e
            else:
                _ = self._extract_result(result)
                if hasattr(_, 'status_code'):
                    if _.status_code < 200 and _.status_code >= 300:
                        return _


            self.request = self._get_request(func_args, func_kwargs)

            # validate the stuff
            valid = self.validate()
            if not valid:
                return self._extract_result(result)

            # sending a notification to the user that initiated the action
            if not self.inverse:
                # do the normal thing of getting the user from the request
                if not self.user_after_request:
                    self.user = self._get_user_from_request(self.request)

                # there is no user in the request, so we need to look at the result for a user
                elif (self.user == None) and isinstance(result, tuple):
                    expected_user = result[1]
                    result = result[0]
                    if isinstance(expected_user, CustomUser):
                        self.user = expected_user

            else:
                self.get_inverse_user(self._extract_result(result))

            # we found a user in a request somewhere
            if self.user != None:
                # attach extra stuff to the Notifier class
                self._attach_extras(result)

                user_id = self.user.id
                # where the magic happens
                send_notification.s(user_id, self.trigger, *self.conf_args, **self.conf_kwargs) \
                    .set(countdown=self.countdown) \
                    .set(expires=self.expires) \
                    .delay()

            return self._extract_result(result)

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__

        return wrapper


    def validate(self, *args, **kwargs):
        # list of validation function to run before executing the notification stuff
        # each tuple is the function to run and the expected output
        # if any function does not return the expected output, stop the loop and return False
        to_run = [(self._assert_request, True), (self._assert_method, True)]

        for func in to_run:
            output = func[0]()
            if output != func[1]:
                return False
        return True

    def _extract_result(self, result):
        """
        Checks the result of the decorated function to avoid trying to send a tuple or list.
        """
        if isinstance(result, tuple):
            return result[0]
        else:
            return result

    # helper functions
    def _get_request(self, args, kwargs, raise_exception=False):
        # check the kwargs for a request
        if 'request' in kwargs.keys():
            request = kwargs.get('request')
            self.request = request
            return request
        # check the args for a request
        for arg in args:
            if isinstance(arg, (HttpRequest, Request)):
                # the argument is a request
                self.request = arg
                return arg
        
        # no request was found
        if raise_exception:
            raise NotificationException("Could not identify a request object in the function")

    def _get_user_from_request(self, request):
        user = getattr(request, 'user', None)
        if (user not in [None, ""]) and (not isinstance(user, AnonymousUser)):
            # we have a user
            self.user = user
            return self.user
        return None

    def _attach_extras(self, result):
        """ Attach extra kwargs to the Notifier class based on the outcome of the main function """
        if self.album:
            self.conf_kwargs['album_id'] = get_album_id(result)
        if self.song:
            self.conf_kwargs['song_id'] = get_song_id(result)
        self.conf_kwargs['inverse'] = self.inverse

    def _assert_request(self):
        """ Returns True if self.request is a valid Request instance """
        if isinstance(self.request, (HttpRequest, Request)):
            return True
        return False

    def _assert_method(self):
        """ Return True if the request is in one of the allowed methods """
        if self.methods != []:
            if self.request.method not in self.methods:
                return False

        return True

    def get_inverse_user(self, result, result_index=None):
        steps = self.user_target.split('.')

        obj = result if result_index == None else result[result_index]

        for step in steps:
            obj = take_step(obj, step)

        if isinstance(obj, CustomUser):
            self.user = obj
            return self.user


notifier = NotifierDecorator
