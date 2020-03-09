"""
Created: 6 Mar. 2020
Author: Jordan Prechac
"""

from django.conf import settings

import threading

from revibe.middleware.base import BaseMiddleware
from revibe.utils.urls import replace_url_id

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

        # check to ensure that the request should be saved
        split_url = url.split('/')
        denied_urls = ['/', '/hc/']

        # don't record if not in the cloud
        # only record outside of production
        # don't record certain urls
        # don't record admin urls
        dont_record_request = (not settings.USE_S3) \
            or (settings.DEBUG == True) \
            or (url in denied_urls) \
            or (settings.ADMIN_PATH in split_url)
        if dont_record_request:
            return
        
        # check the url for ID's - either int or uuid
        url = replace_url_id(url)

        # save the request to DynamoDB
        thread = threading.Thread(target=record_request_async, args=[url, method, status_code])
        thread.setDaemon(True)
        thread.start()
        # record_request_async(url, method, status_code) # for testing exceptions

