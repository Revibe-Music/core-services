"""
Created 6 Mar. 2020
Author: Jordan Prechac
"""

# -----------------------------------------------------------------------------

class BaseMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):

        # Code to be executed for each request before
        # the view (and later middleware) are called
        self.before_response(request)

        # -----------------------------------
        response = self.get_response(request)
        # -----------------------------------

        # Code to be executed for each request/response after
        # the view is called
        self.after_response(response, request=request)

        return response
    
    def before_response(self, request):
        """
        Function to define what happens before the response is called
        """
        pass

    def after_response(self, response, request=None):
        """
        Function to define what happens after the response is called
        """
        pass
