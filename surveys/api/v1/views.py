"""
Created: 03 June 2020
Author: Jordan Prechac
"""

from rest_framework import viewsets, permissions, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.core.mail import send_mail
from django.template import Context
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


from revibe._helpers import responses
from revibe.exceptions import api
from revibe._errors.network import ConflictError, ForbiddenError, NotImplementedError, ExpectationFailedError

from accounts.permissions import TokenOrSessionAuthentication
from notifications.decorators import notifier
from surveys.models import ArtistOfTheWeek
from surveys.models import Contact

from .serializers import ArtistOfTheWeekSerializer
from .serializers import ContactSerializer

# -----------------------------------------------------------------------------


class ArtistOfTheWeekViewset(viewsets.ModelViewSet):
    serializer_class = ArtistOfTheWeekSerializer
    permission_classes = [TokenOrSessionAuthentication,]
    required_alternate_scopes = {
        'GET': [["ADMIN"], ["first-party", "artist"]],
        'POST': [["ADMIN"], ["first-party", "artist"]],
        'DELETE': [["ADMIN"], ["first-party", "artist"]]
    }

    def get_queryset(self):
        queryset = ArtistOfTheWeek.objects.filter(user=self.request.user)

        return queryset


    def update(self, request, pk=None, *args, **kwargs):
        raise api.ServiceUnavailableError("Applications cannot be edited. Please contact support@revibe.tech for more information.")

    def destroy(self, request, pk=None, *args, **kwargs):
        raise api.NotImplementedError("Cannot delete application right now. Please contact support@revibe.tech to remove the application.")


@method_decorator(csrf_exempt, name="dispatch")
class ContactViewset(viewsets.ModelViewSet):
    serializer_class = ContactSerializer
    queryset = Contact.objects.all()
    required_alternate_scopes = {
        'GET': [["ADMIN"], ["first-party", "artist"]],
        'POST': [["ADMIN"], ["first-party", "artist"]],
        'DELETE': [["ADMIN"], ["first-party", "artist"]]
    }

    html_message = render_to_string(
        f"surveys/survey_report.html",
        {
            'first': Contact.first,
            'last': Contact.last,
            'subject': Contact.subject,
            'email': Contact.email,
            'message': Contact.message,
            'date_created': Contact.date_created,
        })

    # post function of contact request
    @api_view(['POST'])
    @permission_classes([permissions.AllowAny])
    def contact(self, request, *args, **kwargs):
        if request.method == 'POST':
            try:
                send_mail(
                    subject="New Contact Form Submitted at revibe.tech",
                    message="",
                    from_email='"Revibe Contact Submission" <noreply@revibe.tech>',
                    recipient_list=[
                        'dev@revibe.tech'
                    ],
                    fail_silently=True,
                    html_message="html_message",
                )
            except Exception:
                pass

    
