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
from django.urls import path, include

from logging import getLogger
logger = getLogger(__name__)

from administration.views import base

# -----------------------------------------------------------------------------

v1_urls = [
    path('account/', include('accounts.urls.v1')),
    path('administration/', include('administration.urls.v1')),
    path('content/', include('content.urls.v1')),
    path('marketplace/', include('marketplace.urls.v1')),
    path('metrics/', include('metrics.urls.v1')),
    path('music/', include('music.urls.v1')),
    path('storage/', include('cloud_storage.urls.v1')),
]

admin_path = settings.ADMIN_PATH

urlpatterns = [
    path(admin_path, admin.site.urls, name="admin"),
    path('jet/', include('jet.urls', namespace="jet")),
    path('jet/dashboard/', include('jet.dashboard.urls', namespace='jet-dashboard')),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('hc/', base.home, name="health_check"),
    path('v1/', include(v1_urls)),
]
