"""
Created: 07 May 2020
Author: Jordan Prechac
"""

# from django.core.mail import send_mail

from revibe._helpers import const

from administration.utils import retrieve_variable

# -----------------------------------------------------------------------------

base_email_config = {
    # links
    "home_website": retrieve_variable("home_website", "https://revibe.tech/"),
    "artist_website": retrieve_variable("artist_website": "https://artist.revibe.tech/"),
    "api_website": retrieve_variable("api_website": "https://api.revibe.tech/"),

    # images
    "revibe_medium_image": const.REVIBE_MEDIUM_IMAGE,
    "youtube_image": const.YOUTUBE_IMAGE,
    "twitter_image": const.TWITTER_IMAGE,
    "facebook_image": const.FACEBOOK_IMAGE,
    "instagram_image": const.INSTAGRAM_IMAGE,

    # contact
    "support_email": const.SUPPORT_EMAIL,
}

