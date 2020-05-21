"""
Created: 21 May 2020
Author: Jordan Prechac
"""

from revibe.decorators import BaseRequestDecorator

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
            if self.request.method.upper() not in self.methods:
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


attributor = AttributionDecorator
