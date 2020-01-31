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
            {"name": 'accounts.customuser', "label": _("Users")},
            {"name": 'accounts.profile'},
            {"name": "accounts.social"}
        ]
    },
    {
        "label": _("Artists and Content"),
        "items": [
            {"name": 'content.artist'},
            {"name": 'accounts.artistprofile'},
            {"name": 'accounts.customuser', "label": _("Users")},
            {"name": 'content.album'},
            {"name": 'content.song'},
            {"name": 'content.albumcontributor'},
            {"name": 'content.songcontributor'}
        ]
    },
    # {
    #     "app_label": _("content"), 
    #     "items": [
    #         {"name": "artist"},
    #         {"name": "album"},
    #         {"name": "image"},
    #         {"name": "song"},
    #         {"name": "track"},
    #         {"name": "albumcontributor"},
    #         {"name": "songcontributor"}
    #     ]
    # },
    {
        "label": _("Files"),
        "items": [
            {"name":"content.image"},
            {"name": "content.track"},
        ]
    },
    {
        "label": _("External Links"), # TODO: make these links work
        "items": [
            {"label": _("API Docs"), "url": _("https://documenter.getpostman.com/view/6267328/SWEB1ah6?version=latest")},
            {"label": _("Artist Portal"), "url": _("https://artist.revibe.tech")},
        ]
    }
]