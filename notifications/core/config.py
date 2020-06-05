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
    "artist_website_stats": retrieve_variable("artist-portal-link-stats", "https://artist.revibe.tech/dashboard/stats"),
    "artist_website_tracks": retrieve_variable("artist-portal-link-tracks", "https://artist.revibe.tech/dashboard/tracks"),
    "artist_website_relink": retrieve_variable("artist-portal-link-relink", "https://artist.revibe.tech/dashboard/relink"),
    "artist_website_account": retrieve_variable("artist-portal-link-account", "https://artist.revibe.tech/dashboard/account"),
    "artist_website_feedback": retrieve_variable("artist-portal-link-feedback", "https://artist.revibe.tech/dashboard/feedback"),

    # images
    "revibe_medium_image": const.REVIBE_MEDIUM_IMAGE,
    "youtube_image": const.YOUTUBE_IMAGE,
    "twitter_image": const.TWITTER_IMAGE,
    "facebook_image": const.FACEBOOK_IMAGE,
    "instagram_image": const.INSTAGRAM_IMAGE,

    # contact
    "support_email": retrieve_variable("support_email", getattr(const, 'SUPPORT_EMAIL', 'support@revibe.tech')),

    # footer # TODO
    "current_year": datetime.datetime.now().year,
    "current_month": datetime.datetime.now().month,
    "current_month_name": datetime.datetime.now().strftime("%B"),
    "current_month_name_abr": datetime.datetime.now().strftime("%b"),
    "current_day": datetime.datetime.now().day,
    "company_name": "Revibe",
    # TODO: mailing address
    # TODO: update preferences link
}

