# from django.urls import path
# from django.conf.urls import include
# from rest_framework import routers
# from .api import AccountViewSet, RegistrationAPI, LoginAPI, AccountAPI
# from knox import views as knox_views
# router = routers.DefaultRouter()
# router.register('accounts', AccountViewSet, 'accounts')
# urlpatterns = [
#     path("", include(router.urls)),
#     path("auth/register/", RegistrationAPI.as_view()),
#     path("auth/account/", AccountAPI.as_view()),
#     path("auth/login/", LoginAPI.as_view()),
#     path("auth/logout/", knox_views.LogoutView.as_view()),
#     path("auth/logoutall/", knox_views.LogoutAllView.as_view()),
# ]