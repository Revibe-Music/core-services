"""
"""


from django.template.context import Context
from django.template.base import Template

# -----------------------------------------------------------------------------

def render_html(template_string, context_dict={}):
    template = Template(template_string)
    context = Context(context_dict)

    return template.render(context)


