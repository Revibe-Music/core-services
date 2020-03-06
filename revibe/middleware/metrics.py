"""
Created: 6 Mar. 2020
Author: Jordan Prechac
"""

from django.conf import settings
from revibe.middleware.base import BaseMiddleware

from metrics.models import Request

# -----------------------------------------------------------------------------

class RequestMetricsMiddleware(BaseMiddleware):
    # def before_response(self, request):
    #     self.m_url = str(request.path)
    #     self.m_method = str(request.method)
    #     # get the request url and method for after_response

    def after_response(self, response, request=None):
        # get the response status code
        url = str(request.path)
        method = str(request.method)
        status_code = str(response.status_code)
        print("Request url: " + url)
        print("Request method: " + method)
        print("Response status code: " + status_code)

        # save the request to DynamoDB
        try:
            if settings.USE_S3:
                new_request = Request(
                    url,
                    method=method,
                    status_code=status_code
                )
                new_request.save()
        except Exception as e:
            print(e)
            raise e

