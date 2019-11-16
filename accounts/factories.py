from oauth2_provider.models import AccessToken, RefreshToken
from . import models
from faker import Faker


class CustomUserFactory(factory.Factory):
    class Meta:
        model = models.CustomUser

class ProfileFactory(factory.Factory):
    class Meta:
        model = models.Profile

class AccessTokenFactory(factory.Factory):
    class Meta:
        model = AccessToken

class RefreshTokenFactory(factory.Factory):
    class Meta:
        model = RefreshToken
