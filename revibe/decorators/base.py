"""
Created: 21 May 2020
Author: Jordan Prechac
"""

from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest
from rest_framework.request import Request

from revibe.exceptions import RevibeException

# -----------------------------------------------------------------------------

class BaseRequestDecorator:

    def __call__(self, func):
        def wrapper(*func_args, **func_kwargs):
            # execute the function
            result = func(*func_args, **func_kwargs)

            # check for a proper status code in the response
            _ = self._extract_result(result)
            if hasattr(_, 'status_code'):
                if _.status_code < 200 or _.status_code >= 300:
                    return _
            self._result = result

            # do the decorator stuff
            try:
                self.execute_wrapping(func_args, func_kwargs)
            except Exception as e:
                print(f"Error wrapping function '{func.__name__}' with decorator '{self.__class__.__name__}'. Exception: {e}")

            # return the original result
            return self._extract_result(self._result)

        # set function meta info
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__

        return wrapper

    def execute_wrapping(self, func_args, func_kwargs):
        raise NotImplementedError()


    def _extract_result(self, result):
        if isinstance(result, tuple):
            return result[0]
        else:
            return result
    
    def _get_user_from_request(self, request):
        user = getattr(request, 'user', None)
        if (user not in [None, '']) and (not isinstance(user, AnonymousUser)):
            self.user = user
            return self.user
        return None
    
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
        
        if raise_exception:
            raise RevibeException("Could not identify a request object in the function")
