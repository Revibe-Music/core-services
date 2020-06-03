"""
Created: 03 June 2020
Author: Jordan Prechac
"""

from django.urls import path, include

# -----------------------------------------------------------------------------


v1_urls = [
    path('account/', include('accounts.urls.v1')),
    path('administration/', include('administration.urls.v1')),
    path('content/', include('content.urls.v1')),
    path('marketplace/', include('marketplace.urls.v1')),
    path('metrics/', include('metrics.urls.v1')),
    path('music/', include('music.urls.v1')),
    path('storage/', include('cloud_storage.urls.v1')),
    path('surveys/', include('surveys.api.v1.urls')), # this is the new standard for api urls
]

v2_urls = []

urlpatterns = [
    path("v1/", include(v1_urls)),
]
