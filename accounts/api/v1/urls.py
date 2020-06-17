from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from allauth.socialaccount.providers.oauth2.views import OAuth2CallbackView

from . import views
# from knox import views as knox_views

router = routers.DefaultRouter()
# router.register("user", v1.AuthenticationViewSet, "user")
router.register("artist", views.UserArtistViewSet, "artistaccount") # artist portal ONLY
router.register("artist/analytics", views.ArtistAnalyticsViewSet, "artist-analytics")
router.register("linked-accounts", views.UserLinkedAccounts, 'linked_accounts')
router.register("profile", views.UserViewSet, "profile")


# artist_urls = [
#     path("", views.UserArtistViewSet.as_view(views_reference.UserArtistViewSet_actions)),
#     path("album/", views.UserArtistViewSet.as_view(views_reference.UserArtistViewSet_albums_actions)),
#     path("song/", views.UserArtistViewSet.as_view(views_reference.UserArtistViewSet_songs_actions)),
# ]


urlpatterns = [

    path("", include(router.urls)),
    path('allauth/', include('allauth.urls')),
    path("register/", views.RegistrationAPI.as_view(), name="register"),
    path("login/", views.LoginAPI.as_view(), name="login"),
    path('logout/', views.LogoutAPI.as_view(), name="logout"),
    path('logout-all/', views.LogoutAllAPI.as_view(), name="logout-all"),
    path('refresh-token/', views.RefreshTokenAPI.as_view(), name="refresh-token"),
    # path("profile/", views.UserViewSet.as_view(), name="profile"),
    path('spotify-authentication/', views.SpotifyConnect.as_view()),
    path('spotify-refresh/', views.SpotifyRefresh.as_view()),
    path('spotify-logout/', views.SpotifyLogout.as_view()),
    path('send-email', views.SendRegisterLink.as_view(), name="send-email"),

    # social authentication
    path("google-authentication/", views.GoogleLoginWeb.as_view(), name="google-login"), # needs to be deprecated!
    path("google-authentication/web/", views.GoogleLoginWeb.as_view(), name="google-login-web"),
    path("google-authentication/mobile/", views.GoogleLoginMobile.as_view(), name="google-login-mobile"),
    path("google-authentication/callback/web/", OAuth2CallbackView.adapter_view(views.GoogleOAuth2AdapterWeb), name="google-callback-web"),
    path("google-authentication/callback/mobile/", OAuth2CallbackView.adapter_view(views.GoogleOAuth2AdapterMobile), name="google-callback-mobile"),

    path("facebook-authentication/", views.FacebookLogin.as_view(), name="facebook-login"),
    path("facebook-authentication/callback/", OAuth2CallbackView.adapter_view(views.FacebookOAuth2Adapter), name="facebook-callback"),

    path('profile/reset-password/', views.view_reset_password, name='reset-password'),

    # referrals
    path("referrals/", include('accounts.referrals.api.v1.urls')),
]
