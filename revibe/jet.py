"""
Created 30 Jan, 2020
Author: Jordan Prechac
"""

from django.utils.translation import gettext_lazy as _

# -----------------------------------------------------------------------------

themes = [
    {
        'theme': 'default', # theme folder name
        'color': '#47bac1', # color of the theme's button in user menu
        'title': 'Default' # theme title
    },
    {
        'theme': 'revibe',
        'color': '#8e36a6', # revoilet
        'title': 'Revibe Classic'
    },
    {
        'theme': 'green',
        'color': '#44b78b',
        'title': 'Green'
    },
    {
        'theme': 'light-green',
        'color': '#2faa60',
        'title': 'Light Green'
    },
    {
        'theme': 'light-violet',
        'color': '#a464c4',
        'title': 'Light Violet'
    },
    {
        'theme': 'light-blue',
        'color': '#5EADDE',
        'title': 'Light Blue'
    },
    {
        'theme': 'light-gray',
        'color': '#222',
        'title': 'Light Gray'
    }
]


side_menu = [ # A list of application or custom item dicts
    {
        "label": _("Accounts"),
        'items': [
            {"name": 'content.artist'},
            {"name": 'accounts.artistprofile'},
            {"name": 'auth.group'},
            {"name": 'accounts.profile'},
            {"name": "accounts.social"},
            {"name": 'accounts.customuser', "label": _("Users")},
        ]
    },
    {
        "label": _("Accounts - Referrals"),
        "items": [
            {"name": 'referrals.pointcategory'},
            {"name": 'referrals.point'},
            {"name": 'referrals.referral'},
        ]
    },
    {
        "label": _("Administration"),
        "items": [
            {"name": 'administration.artistspotlight'},
            {"name": 'administration.blog'},
            {"name": 'administration.campaign'},
            {"name": 'administration.contactform'},
            # {"name": 'administration.alert'},
            {"name": 'administration.variable'},
            {"name": 'administration.youtubekey'},
        ]
    },
    # {
    #     "label": _("Communications"),
    #     "items": [
    #         {"name": 'communication.chat'},
    #         {"name": 'communication.message'},
    #     ]
    # },
    {
        "label": _("Content"),
        "items": [
            {"name": 'content.artist'},
            {"name": 'content.album'},
            {"name": 'content.song'},
            {"name": 'content.albumcontributor'},
            {"name": 'content.songcontributor'},
            {"name": "content.image"},
            {"name": "content.track"},
        ]
    },
    {
        "label": _("Customer Success"),
        "items": [
            {"name": 'customer_success.pathway'},
            {"name": 'customer_success.action'},
            {"name": 'customer_success.pathwayaction'},
            {"name": 'customer_success.actiontaken'},
        ]
    },
    # {
    #     "label": _("Marketplace"),
    #     "items": [
    #         {"name": 'marketplace.good'},
    #         {"name": 'marketplace.transaction'},
    #         {"name": 'content.image'},
    #         {"name": 'content.track'},
    #     ],
    # },
    {
        "label": _("Metrics"),
        "items": [
            # {"name": 'metrics.artistpublicurlclick'},
            # {"name": 'metrics.appsession'},
            {"name": 'metrics.search'},
            {"name": 'metrics.stream'},
        ]
    },
    {
        "label": _("Music"),
        "items": [
            {"name": 'music.playlist'},
            {"name": 'music.library'},
        ]
    },
    {
        "label": _("Notifications"),
        "items": [
            {"name": 'notifications.externalevent'},
            {"name": 'notifications.temporalevent'},
            {"name": 'notifications.notificationtemplate'},
            {"name": 'notifications.notification'},
        ]
    },
    {
        "label": _("Storage"),
        "items": [
            {"name": 'cloud_storage.file'},
            {"name": 'cloud_storage.fileshare'},
        ]
    },
    {
        "label": _("External Links"),
        "items": [
            {"label": _("API Docs"), "url": "https://documenter.getpostman.com/view/6267328/SWEB1ah6?version=latest"},
            {"label": _("Website"), "url": "https://revibe.tech"},
            {"label": _("Artist Portal"), "url": "https://artist.revibe.tech"},
        ]
    }
]