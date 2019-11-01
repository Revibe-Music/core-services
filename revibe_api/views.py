from .models import *
from rest_framework import viewsets, permissions, generics
from knox.models import AuthToken
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

class ArtistViewSet(viewsets.ModelViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer

class RegistrationAPI(generics.GenericAPIView):
    serializer_class = CreateAccountSerializer
    def post(self, request, *args, **kwargs):
        user = self.get_serializer(data=request.data)
        user.is_valid(raise_exception=True)
        user.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })

# class LoginAPI(generics.GenericAPIView):
#     #permission_classes = (permissions.AllowAny,)
#     serializer_class = LoginAccountSerializer
#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data
#         return Response({
#             "user": AccountSerializer(user, context=self.get_serializer_context()).data,
#             "token": AuthToken.objects.create(user)[1]
#         })
