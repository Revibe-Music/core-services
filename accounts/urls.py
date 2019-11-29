from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from . import views
from . import view_reference
# from knox import views as knox_views

router = routers.DefaultRouter()
router.register("linked-accounts", views.UserLinkedAccounts, 'linked_accounts')


artist_urls = [
    path("", views.UserArtistViewSet.as_view(view_reference.UserArtistViewSet_actions)),
    path("album/", views.UserArtistViewSet.as_view(view_reference.UserArtistViewSet_albums_actions)),
    path("song/", views.UserArtistViewSet.as_view(view_reference.UserArtistViewSet_songs_actions)),
]


urlpatterns = [

    path("", include(router.urls)),
    path('allauth/', include('allauth.urls'), name='socialaccount_signup'),
    path("register/", views.RegistrationAPI.as_view()),
    path("login/", views.LoginAPI.as_view()),
    path('logout/', views.LogoutAPI.as_view()),
    path('logout-all/', views.LogoutAllAPI.as_view()),
    path('token/refresh/', views.RefreshTokenAPI.as_view()),
    path("profile/", views.UserViewSet.as_view()),
    path('spotify-authentication/', views.SpotifyConnect.as_view()),
    path('spotify-refresh/', views.SpotifyRefresh.as_view()),
    path('spotify-logout/', views.SpotifyLogout.as_view()),
    # path("linked-accounts/", views.UserLinkedAccounts.as_view()),
    path("artist/", include(artist_urls), name="artist_account"),
]
