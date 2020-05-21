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
