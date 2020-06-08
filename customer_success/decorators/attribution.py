"""
Created: 21 May 2020
Author: Jordan Prechac
"""

import json

from revibe.decorators import BaseRequestDecorator
from revibe.utils.params import get_url_param

from accounts.models import CustomUser
from customer_success.models import Action
from customer_success.tasks import attribute_action
from notifications.utils.objects import take_step

# -----------------------------------------------------------------------------

class AttributionDecorator(BaseRequestDecorator):
    def __init__(self, name, methods=[], countdown=1, user_target=None, *conf_args, **conf_kwargs):
        self.conf_args = conf_args
        self.conf_kwargs = conf_kwargs

        self.name = name
        self.methods = [m.upper() for m in methods]

        # Celery task stuff
        self.countdown = countdown

        self.user = None
        self.request = None

        if user_target:
            self.inverse = True
            self.user_target = user_target
        else:
            self.inverse = False


    def execute_wrapping(self, func_args, func_kwargs):
        # get the request object
        self.request = self._get_request(func_args, func_kwargs)

        # perform validation
        valid = self.validate()
        if not valid:
            return self._extract_result(self._result)

        # get the user
        if not self.inverse:
            self._get_user_from_request(self.request)
        else:
            self.get_inverse_user(self._extract_result(self._result))

        # if user if found, attribute the notification to the action taken
        if self.user != None:

            user_id = self.user.id
            # trigger the Celery task to run
            attribute_action.s(user_id, self.name, *self.conf_args, **self.conf_kwargs) \
                .set(countdown=self.countdown) \
                .delay()


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
        """
        Notes


        Computation steps
        1. check the action's param kwargs against the request parameters
        2. check the action's body kwargs against the request body

        In each step:
            a. load the field from JSON
            b. if the kwargs are empty, skip it
            c. check all of the body/params against the requirements in the model
        
        if anything doesn't check out, return False
        """
        # 1. 
        # 1a. 
        kwargs_json = self.action.required_request_params_kwargs
        try:
            kwargs = json.loads(kwargs_json)
        except Exception:
            return True

        # 1b. skip the stuff if there are no kwargs
        if kwargs != {}:
            # for each kwarg, check the params for that value. If the value is suppose to be None, the kwargs can be empty
            params = self.request.query_params
            # 1c. 
            for key, value in kwargs.items():
                param = get_url_param(params, key, None)

                # if it's a list or a tuple of good values, check that the param is in the list
                # otherwise, check for equality
                valid = param in value if isinstance(value, (list, tuple)) else param == value

                if not valid:
                    return False

        # 2. 
        # 2a.
        kwargs_json = self.action.required_request_body_kwargs
        try:
            kwargs = json.loads(kwargs_json)
        except Exception:
            return False

        # 2b. skip the stuff if there are no kwargs
        if kwargs != {}:
            body = self.request.data
            # 2c. 
            for key, value in kwargs.items():
                body_kwarg = body.get(key, None)

                valid = body_kwarg in value if isinstance(value, (list, tuple)) else body_kwarg == value

                if not valid:
                    return False

        return True

    def get_inverse_user(self, result):
        steps = self.user_target.split('.')
        obj = result

        for step in steps:
            obj = take_step(obj, step)

        if isinstance(obj, CustomUser):
            self.user = obj
            return self.user



attributor = AttributionDecorator
