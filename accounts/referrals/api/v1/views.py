"""
"""

from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action

from revibe._helpers import responses
from revibe.exceptions import api

from accounts.models import CustomUser
from accounts.permissions import TokenOrSessionAuthentication
from accounts.referrals.exceptions import ReferralException
from accounts.referrals.models import Point, Referral
from accounts.referrals.utils.models.point import get_total_points
from notifications.decorators import notifier

from .serializers import PointSerializer, ReferralSerializer

# -----------------------------------------------------------------------------


class ReferralViewset(viewsets.ModelViewSet):
    serializer_class = ReferralSerializer
    permission_classes = [TokenOrSessionAuthentication]
    required_alternate_scopes = {
        "GET": [["ADMIN"], ["first-party"]],
        "POST": [["ADMIN"], ["first-party"]],
    }

    def get_queryset(self):
        user = self.request.user
        return Referral.objects.filter(
            Q(referrer=user) | Q(referree=user)
        )

    # disable some things
    def update(self, request, pk=None, *args, **kwargs):
        raise api.ServiceUnavailableError("Referrals cannot be edited. Please email support@revibe.tech for assistance")
    def destroy(self, request, pk=None, *args, **kwargs):
        raise api.ServiceUnavailableError("Referrals cannot be deleted. Please email support@revibe.tech for assistance")

    @notifier(
        trigger='post-registration-referral-inverse', user_target='data.user_id',
        force=True, check_first=True
    )
    @notifier(
        trigger='post-registration-referral',
        force=True
    )
    def create(self, request, *args, **kwargs):
        data = dict(request.data)

        # check if the request had a user ID or a username
        is_user_id = bool(data.get('user_id', None))
        is_username = bool(data.get('username', None))
        if not (is_user_id or is_username):
            raise api.BadRequestError("Either 'username' or 'user_id' must be included")

        if is_username:
            username = data.pop('username', None)

            try:
                data['user_id'] = CustomUser.objects.get(username=username).id
            except CustomUser.DoesNotExist:
                raise api.NotFoundError(f"A user with username '{username}' could not be found")

        # create the object via the serializer
        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            raise api.BadRequestError(serializer.errors)

        try:
            serializer.save()
        except ReferralException as e:
            raise api.ConflictError(str(e))

        return responses.CREATED(serializer=serializer)


class PointViewset(viewsets.ModelViewSet):
    serializer_class = PointSerializer
    permission_classes = [TokenOrSessionAuthentication,]
    required_alternate_scopes = {
        "GET": [["ADMIN"], ['first-party']]
    }

    def get_queryset(self):
        user = self.request.user
        return Point.objects.get_user_points(user)

    def create(self, request, *args, **kwargs):
        raise api.NotImplementedError("Cannot create points")
    def update(self, request, pk=None, *args, **kwargs):
        raise api.NotImplementedError("Cannot edit points")
    def destroy(self, request, pk=None, *args, **kwargs):
        raise api.NotImplementedError("Cannot delete points")

    @action(detail=False, methods=['get'], url_path='total', url_name='total-points')
    def total_points(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = get_total_points(queryset)

        return responses.OK(data=data)

