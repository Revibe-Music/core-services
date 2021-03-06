"""
"""

from django.urls import path, include
from rest_framework import routers

from . import views

# -----------------------------------------------------------------------------


router = routers.DefaultRouter()
router.register("my-referrals", views.ReferralViewset, "my-referrals")
router.register("points", views.PointViewset, "points")

urlpatterns = [
    path("", include(router.urls))
]

