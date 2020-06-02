"""
Created: 07 May 2020
Author: Jordan Prechac
"""

# from django.core.mail import send_mail

from revibe._helpers import const

import datetime

from administration.utils import retrieve_variable

# -----------------------------------------------------------------------------

base_email_config = {
    # links
    "home_website": retrieve_variable("home_website", "https://revibe.tech/"),
    "artist_website": retrieve_variable("artist_website", "https://artist.revibe.tech/"),
    "api_website": retrieve_variable("api_website", "https://api.revibe.tech/"),

    # images
    "revibe_medium_image": const.REVIBE_MEDIUM_IMAGE,
    "youtube_image": const.YOUTUBE_IMAGE,
    "twitter_image": const.TWITTER_IMAGE,
    "facebook_image": const.FACEBOOK_IMAGE,
    "instagram_image": const.INSTAGRAM_IMAGE,

    # contact
    "support_email": retrieve_variable("support_email", getattr(const, 'SUPPORT_EMAIL', 'support@revibe.tech')),

    # footer # TODO
    # current_year: 
    # company_name
    # mailing address
    # update preferences link
}

