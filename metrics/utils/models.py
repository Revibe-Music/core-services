"""
Created: 4 Mar. 2020
Author: Jordan Prechac
"""

from django.db import connection

import gc
import threading

from accounts.models import CustomUser
from metrics.models import Search

# -----------------------------------------------------------------------------

def record_search_async(user, search_text):
    """
    """
    user_id = str(user.id)

    def record_search(user_id, search_text):
        """
        """
        # get the user object
        user = CustomUser.objects.get(id=user_id)

        # set the search
        search = Search.objects.create(user=user, search_text=search_text)

        # close out the thread
        gc.collect()
        connection.close()

    t = threading.Thread(target=record_search, args=[user_id, search_text])
    t.setDaemon(True)
    t.start()

def record_request_async():
    pass

