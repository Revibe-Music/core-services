"""
Created: 08 May 2020
Author: Jordan Prechac
"""

from django.http import HttpRequest
from rest_framework.request import Request

import json

import logging
logger = logging.getLogger(__name__)

from revibe.decorators import BaseRequestDecorator
from revibe.utils.params import get_url_param, get_request_header

from accounts.models import CustomUser
from notifications.models import Event

from .exceptions import NotificationException
from .tasks import send_notification
from .utils.objects import get_album_id, get_song_id, take_step

# -----------------------------------------------------------------------------

one_hour = 60*60

class NotifierDecorator(BaseRequestDecorator):
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

    def __init__(self, trigger, user_target=None, methods=[], user_after_request=False, album=False, song=False, contribution=False, countdown=1, expires=one_hour, *conf_args, **conf_kwargs):
        self.trigger = trigger
        self.user_after_request = user_after_request
        self.album = album
        self.song = song
        self.contribution = contribution
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
        
        self.before_call_funcs = [
            (self._get_event, [self.trigger], {}), 
        ]


    def execute_wrapping(self, func_args, func_kwargs):
        self.request = self._get_request(func_args, func_kwargs)

        # validate the stuff
        valid = self.validate()
        if not valid:
            return self._extract_result(self._result)

        # sending a notification to the user that initiated the action
        if not self.inverse:
            # do the normal thing of getting the user from the request
            if not self.user_after_request:
                self.user = self._get_user_from_request(self.request)

            # there is no user in the request, so we need to look at the result for a user
            elif (self.user == None) and isinstance(self._result, tuple):
                expected_user = self._result[1]
                if isinstance(expected_user, CustomUser):
                    self.user = expected_user

        else:
            self.get_inverse_user(self._extract_result(self._result))

        # we found a user in a request somewhere
        if self.user != None:
            # attach extra stuff to the Notifier class
            self._attach_extras(self._result)

            user_id = self.user.id
            # where the magic happens
            send_notification.s(user_id, self.trigger, *self.conf_args, **self.conf_kwargs) \
                .set(countdown=self.countdown) \
                .set(expires=self.expires) \
                .delay()

        return self._extract_result(self._result)


    def validate(self, *args, **kwargs):
        # list of validation function to run before executing the notification stuff
        # each tuple is the function to run and the expected output
        # if any function does not return the expected output, stop the loop and return False
        to_run = [(self._assert_event, True), (self._assert_request, True), (self._assert_method, True), (self._perform_model_validation, True),]

        for func in to_run:
            output = func[0]()
            if output != func[1]:
                return False
        return True

    def _attach_extras(self, result):
        """ Attach extra kwargs to the Notifier class based on the outcome of the main function """
        data = result.data
        if self.album:
            self.conf_kwargs['album_id'] = get_album_id(data)
        if self.song:
            self.conf_kwargs['song_id'] = get_song_id(data)
        if self.contribution:
            self.conf_kwargs['contribution'] = getattr(self._extract_result(self._result), 'data', None)
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

    def _assert_event(self):
        if self.event == None:
            return False
        elif isinstance(self.event, Event):
            return True
        return False

    def _perform_model_validation(self):
        """  """
        # check params
        kwargs_json = self.event.required_request_params
        if kwargs_json != "{}":
            try:
                kwargs = json.loads(kwargs_json)
            except Exception as err:
                logger.warn(f"Failed to load kwargs as json. Exception: {str(err)}")
                return True
        
            params = self.request.query_params

            for key, value in kwargs.items():
                param = get_url_param(params, key, None)

                valid = (param in value) if isinstance(value, (list, tuple)) else (param == value)

                if not valid:
                    return False
        
        # check headers
        kwargs_json = self.event.required_request_headers
        if kwargs_json != "{}":
            try:
                kwargs = json.loads(kwargs_json)
            except Exception as err:
                logger.warn(f"Failed to load kwargs as json. Exception: {str(err)}")
                return True
            
            headers = self.request.META

            for key, value in kwargs.items():
                header = get_request_header(request, key, None)

                valid = (header in value) if isinstance(value, (list, tuple)) else (param == value)

                if not valid:
                    return False

        # check request body
        kwargs_json = self.event.required_request_body
        if kwargs_json != "{}":
            try:
                kwargs = json.loads(kwargs_json)
            except Exception as err:
                logger.warn(f"Failed to load kwargs as json. Exception: {str(err)}")
                return True
            
            body = dict(request.body)

            for key, value in kwargs.items():
                b = body.get(key, None)
                valid = (b in value) if isinstance(value, (list, tuple)) else (b == value)

                if not valid:
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

    def _get_event(self, trigger=None):
        trigger = trigger if trigger else self.trigger
        event = Event.objects.filter(active=True, trigger=trigger)

        if event.exists():
            self.event = event.first()
            return self.event

        return None


notifier = NotifierDecorator
