"""
Created: 16 Mar. 2020
Author: Jordan Prechac
"""

from revibe.utils.urls import add_query_params

from administration.utils.models import retrieve_variable

# -----------------------------------------------------------------------------

def generate_sharing_link(user):
    """
    """
    base_url = retrieve_variable('mobile_app_share_link', "https://apps.apple.com/us/app/revibe-music/id1500839967")
    params = {"uid": str(user.id)}
    final_url = add_query_params(base_url, params)

    return final_url
