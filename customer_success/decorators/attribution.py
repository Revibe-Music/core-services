"""
Created: 21 May 2020
Author: Jordan Prechac
"""

import json

from revibe.decorators import BaseRequestDecorator
from revibe.utils.params import get_url_param

from customer_success.models import Action
from customer_success.tasks import attribute_action

# -----------------------------------------------------------------------------

class AttributionDecorator(BaseRequestDecorator):
    def __init__(self, name, methods=[], countdown=1, *conf_args, **conf_kwargs):
        self.conf_args = conf_args
        self.conf_kwargs = conf_kwargs

        self.name = name
        self.methods = [m.upper() for m in methods]

        # Celery task stuff
        self.countdown = countdown

        self.user = None
        self.request = None


    def __call__(self, func):

        def wrapper(*func_args, **func_kwargs):
            # execute function,
            # if exception or bad status code, return that
            # instead of running the decorator stuff
            try:
                result = func(*func_args, **func_kwargs)
            except Exception as e:
                raise e
            else:
                _ = self._extract_result(result)
                if hasattr(_, 'status_code'):
                    if _.status_code < 200 or _.status_code >= 300:
                        return _
                self._result = result


            # get the request object
            self.request = self._get_request(func_args, func_kwargs)

            # perform validation
            valid = self.validate()
            if not valid:
                return self._extract_result(self._result)

            # get the user
            self._get_user_from_request(self.request)

            # if user if found, attribute the notification to the action taken
            if self.user != None:

                user_id = self.user.id
                # trigger the Celery task to run
                attribute_action.s(user_id, self.name, *self.conf_args, **self.conf_kwargs) \
                    .set(countdown=self.countdown) \
                    .delay()

            # return the result of the original function
            return self._extract_result(self._result)

        # set function meta info
        wrapper.__name__ = func.__name__
        wrapper.__doc__  = func.__doc__

        return wrapper
    
    def validate(self):
        to_run = [(self._assert_method, True), (self._get_action, True), (self._assert_request_kwargs, True), ]

        for func in to_run:
            output = func[0]()
            if output != func[1]:
                return False
        return True


    def _assert_method(self):
        if self.methods != []:
            if self.request.method not in self.methods:
                return False
        
        return True

    def _get_action(self):
        try:
            action = Action.objects.filter(active=True).get(name=self.name)
        except Action.DoesNotExist:
            return False
        
        self.action = action
        return True

    def _assert_request_kwargs(self):
        kwargs_json = self.action.required_request_params_kwargs
        try:
            kwargs = json.loads(kwargs_json)
        except Exception:
            return True

        # skip the stuff if there are no kwargs
        if kwargs == {}:
            return True
        
        # for each kwarg, check the params for that value. If the value is suppose to be None, the kwargs can be empty
        params = self.request.query_params
        for key, value in kwargs.items():
            param = get_url_param(params, key, None)

            # if it's a list or a tuple of good values, check that the param is in the list
            # otherwise, check for equality
            valid = param in value if isinstance(value, (list, tuple)) else param == value

            if not valid:
                return False
        
        return True


attributor = AttributionDecorator
