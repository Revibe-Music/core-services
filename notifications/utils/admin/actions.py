"""
Created 15 May 2020
Author: Jordan Prechac
"""

# -----------------------------------------------------------------------------


def activate_events(modeladmin, request, queryset):
    queryset.update(active=True)
activate_events.short_description = "Activate selected events"

def deactivate_events(modeladmin, request, queryset):
    queryset.update(active=False)
deactivate_events.short_description = "Deactivate selected events"


def convert_type(modeladmin, request, queryset):
    if queryset.first().type == 'external':
        new = 'temporal'
    else:
        new = 'external'
    
    queryset.update(type=new)
convert_type.short_description = "Swap types"


def activate_templates(modeladmin, request, queryset):
    queryset.update(active=True)
activate_templates.short_description = "Activate selected templates"

def deactivate_templates(modeladmin, request, queryset):
    queryset.update(active=False)
deactivate_templates.short_description = "Deactivate selected templates"
