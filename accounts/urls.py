from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from . import views
from knox import views as knox_views

router = routers.DefaultRouter()

urlpatterns = [
    path("", include(router.urls)),
    path("register/", views.RegistrationAPI.as_view()),
    path("login/", views.LoginAPI.as_view()),
    path("logout/", knox_views.LogoutView.as_view()),
    path("logoutall/", knox_views.LogoutAllView.as_view()),
    path("profile/", views.UserViewSet.as_view()),
]
