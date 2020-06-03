"""artist_portal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path, include

from . import api

from administration.views import base

# temp
from communication import views

# -----------------------------------------------------------------------------

admin_path = settings.ADMIN_PATH

urlpatterns = [
    # home path
    path("", base.blank_request, name="home"),

    path(admin_path, admin.site.urls, name="admin"),
    path('jet/', include('jet.urls', namespace="jet")),
    path('jet/dashboard/', include('jet.dashboard.urls', namespace='jet-dashboard')),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('hc/', base.home, name="health_check"),

    # api urls
    path('v1/', include(api.v1_urls)), # TODO: Deprecate these urls
    path('api/', include(api.urlpatterns)),

    # temp
    path('communication/', views.index, name="index"),
    path('communication/<str:room_name>/', views.room,  name="room"),
]
