"""
Created: 10 June 2020
"""

from django.urls import path, re_path, include

from . import views

# -----------------------------------------------------------------------------

urlpatterns = [
    re_path(r"^images/(?P<id>[a-zA-Z0-9-_]+)/$", views.email_image_attribution, name="image-attribution"),
]


