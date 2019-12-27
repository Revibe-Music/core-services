from rest_framework import viewsets
from rest_framework.decorators import action

from accounts.permissions import TokenOrSessionAuthentication
from administration.models import *
from administration.serializers import v1 as adm_ser_v1
from artist_portal._helpers import responses

import logging

logger = logging.getLogger(__name__)


class FormViewSet(viewsets.GenericViewSet):
    queryset = ContactForm.objects.all()
    serializer_class = adm_ser_v1.ContactFormSerializer
    permission_classes = [TokenOrSessionAuthentication]
    required_alternate_scopes = {
        "GET": [["ADMIN"]],
        "POST": [["ADMIN"],["first-party"]],
    }

    @action(detail=False, methods=['post'], url_path="contact-form")
    def contact_form(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return responses.CREATED(serializer)
        else:
            return responses.SERIALIZER_ERROR_RESPONSE(serializer)
        return responses.NO_REQUEST_TYPE()
        
