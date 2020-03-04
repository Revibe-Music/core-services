"""
Created: 4 Mar. 2020
Author: Jordan Prechac
"""

from django.db.models import F, Q

import datetime
import threading

from metrics.models import AppSession

# -----------------------------------------------------------------------------

class MobileAppSessionLoggingMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        # if the request is authenticated, create or add-to a session
        user = getattr(request, 'user', None)
        if user != None and not user.is_anonymous:
            # check if there is an active session for the current user
            # if there is not, create a new one
            session_timeout = datetime.datetime.now() - datetime.timedelta(minutes=20) # minutes
            filter_object = Q(user=user, end_time__gte=session_timeout)
            app_session = AppSession.objects.filter(filter_object).order_by('-end_time')
            sessions_found = app_session.count()

            if sessions_found == 0:
                app_session = AppSession.objects.create(user=user, interactions=1)
            else:
                app_session = app_session.first()
                app_session.interactions = F('interactions') + 0
                app_session.save()

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

