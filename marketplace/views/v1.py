"""
Created: 20 Mar. 2020
Author: Jordan Prechac
"""

from rest_framework import views, viewsets

from accounts.permissions import TokenOrSessionAuthentication

from marketplace.models import Good
from marketplace.serializers import v1 as mkt_ser_v1

# -----------------------------------------------------------------------------

class GoodViewSet(viewsets.ModelViewSet):
    queryset = Good.objects.all()
    serializer_class = mkt_ser_v1.GoodSerializer
    permission_classes = [TokenOrSessionAuthentication]
    required_alternate_scopes = {
        "GET": [["ADMIN"],["first-party"]],
    }
