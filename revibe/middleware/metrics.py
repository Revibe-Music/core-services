"""
Created: 6 Mar. 2020
Author: Jordan Prechac
"""

from django.conf import settings
from revibe.middleware.base import BaseMiddleware

import threading

from metrics.utils.models import record_request_async

# -----------------------------------------------------------------------------

class RequestMetricsMiddleware(BaseMiddleware):
    # def before_response(self, request):
    #     self.m_url = str(request.path)
    #     self.m_method = str(request.method)
    #     # get the request url and method for after_response

    def after_response(self, response, request=None):
        # return # temp stopper
        # get the response status code
        url = str(request.path)
        method = str(request.method)
        status_code = str(response.status_code)
        print("Request url: " + url)
        print("Request method: " + method)
        print("Response status code: " + status_code)

        # save the request to DynamoDB
        if settings.USE_S3 and settings.DEBUG == False:
            thread = threading.Thread(target=record_request_async, args=[url, method, status_code])
            thread.setDaemon(True)
            thread.start()
            # record_request_async(url, method, status_code) # for testing exceptions

