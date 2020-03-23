"""
Created: 20 Mar. 2020
Author: Jordan Prechac
"""

from rest_framework import views, viewsets
from rest_framework.decorators import action

from revibe._errors import network
from revibe._helpers import responses
from revibe.auth.artist import get_authenticated_artist

from accounts.permissions import TokenOrSessionAuthentication
from marketplace.models import Good, Transaction
from marketplace.serializers import v1 as mkt_ser_v1

# -----------------------------------------------------------------------------

class GoodViewSet(viewsets.ModelViewSet):
    queryset = Good.objects.all()
    serializer_class = mkt_ser_v1.GoodSerializer
    permission_classes = [TokenOrSessionAuthentication]
    required_alternate_scopes = {
        "GET": [["ADMIN"],["first-party"]],
    }

    def create(self, request, *args, **kwargs):
        pass
    def update(self, request, *args, **kwargs):
        pass

    def get_current_artist(self, request):
        return get_authenticated_artist(request)

    @action(detail=False, methods=['get', 'post', 'patch', 'delete'], url_path='me', url_name='me')
    def my_marketplace(self, request, *args, **kwargs):
        artist = self.get_current_artist(request)

        if request.method == 'GET':
            goods = self.get_queryset().filter(seller=artist)
            serializer = self.get_serializer(goods, many=True)

            return responses.OK(serializer=serializer)

        elif request.method == 'POST':
            raise network.NotImplementedError

        elif request.method == 'PATCH':
            raise network.NotImplementedError

        elif request.method == 'DELETE': 
            raise network.NotImplementedError

        raise network.BadRequestError


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = mkt_ser_v1.TransactionSerializer
    permission_classes = [TokenOrSessionAuthentication]
    required_alternate_scopes = {
        "GET": [["ADMIN"],["first-party"]],
    }

