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
            {"name": 'auth.group'},
            {"name": 'content.artist'},
            {"name": 'accounts.artistprofile'},
            {"name": "accounts.social"}
        ]
    },
    {
        "label": _("Administration"),
        "items": [
            {"name": 'administration.campaign'},
            {"name": 'administration.alert'},
            {"name": 'administration.blog'},
            {"name": 'administration.contactform'},
            {"name": 'administration.variable'},
            {"name": 'administration.youtubekey'},
        ]
    },
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
        "label": _("Music"),
        "items": [
            {"name": 'music.playlist'},
            {"name": 'music.library'},
        ]
    },
    {
        "label": _("Usage"),
        "items": [
            {"name": 'metrics.stream'},
            {"name": 'metrics.search'},
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