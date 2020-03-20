"""
Created 20 Mar. 2020
Author: Jordan Prechac
"""

from django.urls import path
from django.conf.urls import include
from rest_framework import routers

from marketplace.views import v1

# -----------------------------------------------------------------------------

router = routers.DefaultRouter()
router.register('goods', v1.GoodViewSet, 'goods')

urlpatterns = [
    path("", include(router.urls)),
]
