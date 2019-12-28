from django.urls import path
from django.conf.urls import include
from rest_framework import routers

from administration.views import v1


router = routers.DefaultRouter()
router.register('forms', v1.FormViewSet, 'forms')
router.register('company', v1.CompanyViewSet, 'company')

urlpatterns = [

    path('', include(router.urls)),
]