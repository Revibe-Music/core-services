from django.urls import path
from django.conf.urls import include
from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register('forms', views.FormViewSet, 'forms')
router.register('company', views.CompanyViewSet, 'company')
router.register('youtubekey', views.YouTubeKeyViewSet, 'youtubekey')
router.register('alerts', views.AlertViewSet, 'alerts')
router.register('blog', views.BlogViewSet, 'blog')
router.register('variables', views.StateVariablesView, 'variables')
router.register('surveys', views.SurveyViewSet, 'surveys')

urlpatterns = [
    path('', include(router.urls)),
    path('artistoftheweek/', views.get_artist_of_the_week, name="artist-of-the-week"),
]
