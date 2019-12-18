from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from accounts.views import v1, v1_reference
# from knox import views as knox_views

router = routers.DefaultRouter()
router.register("linked-accounts", v1.UserLinkedAccounts, 'linked_accounts')
router.register("artist", v1.UserArtistViewSet, "artist") # artist portal ONLY


# artist_urls = [
#     path("", v1.UserArtistViewSet.as_view(v1_reference.UserArtistViewSet_actions)),
#     path("album/", v1.UserArtistViewSet.as_view(v1_reference.UserArtistViewSet_albums_actions)),
#     path("song/", v1.UserArtistViewSet.as_view(v1_reference.UserArtistViewSet_songs_actions)),
# ]


urlpatterns = [

    path("", include(router.urls)),
    path('allauth/', include('allauth.urls')),
    path("register/", v1.RegistrationAPI.as_view()),
    path("login/", v1.LoginAPI.as_view()),
    path('logout/', v1.LogoutAPI.as_view()),
    path('logout-all/', v1.LogoutAllAPI.as_view()),
    path('token/refresh/', v1.RefreshTokenAPI.as_view()),
    path("profile/", v1.UserViewSet.as_view()),
    path('spotify-authentication/', v1.SpotifyConnect.as_view()),
    path('spotify-refresh/', v1.SpotifyRefresh.as_view()),
    path('spotify-logout/', v1.SpotifyLogout.as_view()),
    path('artist', v1.UserArtistViewSet, name='user_artist'),
    # path("linked-accounts/", views.UserLinkedAccounts.as_view()),
    # path("artist/", include(artist_urls), name="artist_account"),
]
