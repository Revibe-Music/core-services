from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from allauth.socialaccount.providers.oauth2.views import OAuth2CallbackView

from accounts.views import v1, v1_reference
# from knox import views as knox_views

router = routers.DefaultRouter()
# router.register("user", v1.AuthenticationViewSet, "user")
router.register("artist", v1.UserArtistViewSet, "artistaccount") # artist portal ONLY
router.register("artist/analytics", v1.ArtistAnalyticsViewSet, "artist-analytics")
router.register("linked-accounts", v1.UserLinkedAccounts, 'linked_accounts')
router.register("profile", v1.UserViewSet, "profile")


# artist_urls = [
#     path("", v1.UserArtistViewSet.as_view(v1_reference.UserArtistViewSet_actions)),
#     path("album/", v1.UserArtistViewSet.as_view(v1_reference.UserArtistViewSet_albums_actions)),
#     path("song/", v1.UserArtistViewSet.as_view(v1_reference.UserArtistViewSet_songs_actions)),
# ]


urlpatterns = [

    path("", include(router.urls)),
    path('allauth/', include('allauth.urls')),
    path("register/", v1.RegistrationAPI.as_view(), name="register"),
    path("login/", v1.LoginAPI.as_view(), name="login"),
    path('logout/', v1.LogoutAPI.as_view(), name="logout"),
    path('logout-all/', v1.LogoutAllAPI.as_view(), name="logout-all"),
    path('refresh-token/', v1.RefreshTokenAPI.as_view(), name="refresh-token"),
    # path("profile/", v1.UserViewSet.as_view(), name="profile"),
    path('spotify-authentication/', v1.SpotifyConnect.as_view()),
    path('spotify-refresh/', v1.SpotifyRefresh.as_view()),
    path('spotify-logout/', v1.SpotifyLogout.as_view()),
    path('send-email', v1.SendRegisterLink.as_view(), name="send-email"),

    # social authentication
    path("google-authentication/", v1.GoogleLogin.as_view(), name="google-login"),
    path("google-authentication/callback/", OAuth2CallbackView.adapter_view(v1.GoogleOAuth2Adapter), name="google-callback"),
    path("facebook-authentication/", v1.FacebookLogin.as_view(), name="facebook-login"),
    path("facebook-authentication/callback/", OAuth2CallbackView.adapter_view(v1.FacebookOAuth2Adapter), name="facebook-callback"),

    path('profile/reset-password/', v1.view_reset_password, name='reset-password'),

    # referrals
    path("referrals/", include('accounts.referrals.api.v1.urls')),
]
