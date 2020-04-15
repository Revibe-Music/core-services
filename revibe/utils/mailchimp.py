"""
Created: 19 Mar. 2020
Author: Jordan Prechac
"""

import hashlib
import requests
from requests.auth import HTTPBasicAuth

from administration.utils.models.variable import retrieve_variable

# -----------------------------------------------------------------------------

mailchimp_api_key = retrieve_variable('mailchimp_api_key', '882a0dbeda4d0a1779b865af4125d869-us7')
mailchimp_api_url = "https://us7.api.mailchimp.com/3.0"
mailchimp_list_id = "0acdd15301"
mailchimp_tag_ids = {"Artist": "1407590", "Registered User": "1407602"}

mailchimp_api_list_member_url = f"{mailchimp_api_url}/lists/{mailchimp_list_id}/members"
mailchimp_api_tag_url = f"{mailchimp_api_url}/lists/{mailchimp_list_id}/segments/"

authentication = HTTPBasicAuth('revibe-api', mailchimp_api_key)

def register_tags(email, artist=False):
    url = f"{mailchimp_api_tag_url}/{mailchimp_tag_ids['Registered User']}/members"

    r1 = requests.post(
        url, 
        auth=authentication,
        json={"email_address": email},
        timeout=10
    )

    if artist:
        url = f"{mailchimp_api_tag_url}/{mailchimp_tag_ids['Artist']}/members"
        r2 = requests.post(
            url, 
            auth=authentication,
            json={"email_address": email},
            timeout=10
        )


def add_new_list_member(user):
    """
    """
    email = user.profile.email
    fname = user.first_name
    lname = user.last_name

    data = {
        "email_address": str(email),
        "email_type": "html",
        "status": "subscribed",
    }
    if fname != None and lname != None:
        data['merge_fields'] = {
            "FNAME": fname,
            "LNAME": lname
        }

    r = requests.post(
        mailchimp_api_list_member_url,
        auth=authentication,
        json=data,
        timeout=10
    )

    register_tags(email, artist=False)


def get_sub_hash(email):
    """
    """
    sub_hash = hashlib.md5(email.encode()).hexdigest()
    return sub_hash


def update_list_member(user, artist=False):
    """
    """

    email = user.profile.email
    fname = user.first_name
    lname = user.last_name

    data = {
        "email_address": str(email),
        "email_type": 'html',
        "status": "subscribed",
    }

    if fname != None and lname != None:
        data['merge_fields'] = {
            "FNAME": fname,
            "LNAME": lname
        }

    r = requests.put(
        f"{mailchimp_api_list_member_url}/{get_sub_hash(email)}",
        auth=authentication,
        json=data,
        timeout=10
    )

    register_tags(email, artist=artist)

