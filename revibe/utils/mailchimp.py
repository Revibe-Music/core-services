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
mailchimp_api_list_member_url = f"{mailchimp_api_url}/lists/{mailchimp_list_id}/members"

authentication = HTTPBasicAuth('revibe-api', mailchimp_api_key)

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
        "tags": ["Registered User"],
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

    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(e)
        print(r.status_code)
        print(r.text)


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
        "tags": ["Registered User"]
    }
    if fname != None and lname != None:
        data['merge_fields'] = {
            "FNAME": fname,
            "LNAME": lname
        }
    if artist:
        data['tags'].append("Artist")
    
    r = requests.put(
        f"{mailchimp_api_list_member_url}/{get_sub_hash(email)}",
        auth=authentication,
        json=data,
        timeout=10
    )

    print(r.status_code)
    print(r.text)

