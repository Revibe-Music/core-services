from django.urls import path
from django.conf.urls import include
from rest_framework import routers

from administration.views import v1


router = routers.DefaultRouter()
router.register('forms', v1.FormViewSet, 'forms')
router.register('company', v1.CompanyViewSet, 'company')
router.register('youtubekey', v1.YouTubeKeyViewSet, 'youtubekey')
router.register('alerts', v1.AlertViewSet, 'alerts')
router.register('blog', v1.BlogViewSet, 'blog')
router.register('variables', v1.StateVariablesView, 'variables')

urlpatterns = [
    path('', include(router.urls)),

]
