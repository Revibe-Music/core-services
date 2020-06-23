"""
Created: 23 June 2020
"""

from django import template
from django.apps import apps

from utils.branch import models as branch_models

# -----------------------------------------------------------------------------

register = template.Library()

Variable = apps.get_model('administration', 'Variable')
Template = apps.get_model('notifications', 'NotificationTemplate')

@register.simple_tag(name='deep_link', takes_context=True)
def generate_deep_link(context, obj):
    default_value = "sad" + Variable.objects.retrieve('home_website', 'https://revibe.tech')

    klass_name = obj.__class__.__name__.lower()
    # print("Obj: ", obj)
    # print("Class Name: ", klass_name)
    # print("Type: ", type(obj))

    # return the default if something improper is passed to the obj_type param
    allowed_types = ['song', 'album', 'artist']
    if klass_name not in allowed_types:
        return default_value

    # get the template used
    template = Template.objects.get(id=context['template_id'])

    # find the function, call it, and return that
    func = getattr(branch_models, f"{klass_name}_link_from_template")
    link = func(obj, template)
    return link




