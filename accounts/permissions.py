from django.core.exceptions import ImproperlyConfigured
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission
from oauth2_provider.settings import oauth2_settings

class TokenOrSessionAuthentication(BasePermission):

    def has_permission(self ,request, view):
        token = request.auth

        if (not token) and (request.session.session_key != None): # TODO: NOT A PERMANENT SOLUTION
            return True

        if hasattr(token, "scope"):
            required_alternate_scopes = self.get_scopes(request, view)

            m = request.method.upper()
            if m in required_alternate_scopes:
                for alt in required_alternate_scopes[m]:
                    if token.is_valid(alt):
                        return True
            raise PermissionError("You do not have access for this request type")

        raise PermissionError("Could not identify a session or a request access token")

    def get_scopes(self, request, view):
        try:
            return getattr(view, "required_alternate_scopes")
        except AttributeError:
            raise ImproperlyConfigured("Must specify 'required_alternate_scopes'")

class TokenOrSessionUserPermissions(BasePermission):
    pass
