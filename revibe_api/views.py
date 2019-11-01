from .models import *
from rest_framework import viewsets
from .serializers import *

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    # try:
    #     user = CustomUser.objects.create_user('test2', password='test2', is_staff=True)
    #     user.save()
    # except Exception as e:
    #     print(e)

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer