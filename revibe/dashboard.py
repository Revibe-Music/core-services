"""
author: Jordan Prechac
Created: 3 Feb, 2020
"""

from django.utils.translation import gettext_lazy as _
from jet.dashboard import modules
from jet.dashboard.dashboard import Dashboard, AppIndexDashboard

from revibe._helpers.const import API_DOCS_LINK

# -----------------------------------------------------------------------------

class CustomIndexDashboard(Dashboard):
    columns = 3

    support_list = modules.LinkList(
        _('Support'),
        children=[
            {
                'title': _('Django documentation'),
                'url': 'http://docs.djangoproject.com/',
                'external': True,
            },
            {
                'title': _('API Documentation'),
                'url': API_DOCS_LINK,
                'external': True,
            },
        ],
        column=2,
        order=0
    )

    recent_actions = modules.RecentActions(
        _('Recent Actions'),
        10,
        column=2,
        order=0
    )

    def init_with_context(self, context):
        self.available_children.append(self.support_list)

        self.children.append(modules.AppList(
            _('Apps'),
            exclude=(
                'oauth2_provider.grants',
                'oauth2_provider.applications',
                'rest_auth.*',
                'authtoken.*',
            ),
            column=1,
            order=0
        ))

        self.available_children.append(self.recent_actions)
