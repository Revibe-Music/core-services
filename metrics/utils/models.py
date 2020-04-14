"""
Created: 4 Mar. 2020
Author: Jordan Prechac
"""

from django.conf import settings
from django.db import connection

from datetime import datetime
import gc
import threading

from accounts.models import CustomUser
from metrics.models import Search, Request

# -----------------------------------------------------------------------------

def record_search_async(user, search_text):
    """
    """
    user_id = str(user.id)

    def record_search(user_id, search_text):
        """
        """
        # set the data
        data = {
            "search_text": search_text
        }

        # get the user object
        user = CustomUser.objects.get(id=user_id)
        # check permissions
        if user.profile.allow_search_data:
            data['user'] = user

        # set the search
        search = Search.objects.create(**data)

        # close out the thread
        gc.collect()
        connection.close()

    t = threading.Thread(target=record_search, args=[user_id, search_text])
    t.setDaemon(True)
    t.start()

def record_request_async(url, method, status_code):
    if not settings.USE_S3:
        return

    json = [{
        "method": method,
        "status_code": status_code,
        "timestamp": str(datetime.now())
    },]
    try:
        request = Request.get(url)
        request.update(actions=[
            Request.requests.set(Request.requests.append(json))
        ])
        # above code provided from https://github.com/pynamodb/PynamoDB/issues/434
        request.save()
    except Request.DoesNotExist as dne:
        request = Request(url, requests=json)
        request.save()
    except Exception as e:
        print(e)
        # raise(e)
    
    gc.collect()
    connection.close()

