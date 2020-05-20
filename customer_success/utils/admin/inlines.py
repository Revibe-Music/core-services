"""
Created: 20 May 2020
Author: Jordan Prechac
"""

from django.contrib import admin

from customer_success.models import Action, PathwayAction

from customer_success.utils.admin.forms import PathwayActionInlineForm

# -----------------------------------------------------------------------------


class ExternalEventActionInLine(admin.TabularInline):
    model = Action.extra_events.through
    extra = 1
    verbose_name = "Action Prompt"
    verbose_name_plural = "Action Prompts"


class PathwayActionInline(admin.TabularInline):
    model = PathwayAction
    form  = PathwayActionInlineForm

    extra = 1

    verbose_name = "Pathway Ranking"
    verbose_name_plural = "Pathway Rankings"


