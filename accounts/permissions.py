from django.core.exceptions import ImproperlyConfigured
from rest_framework.permissions import BasePermission
from oauth2_provider.models import AccessToken
from oauth2_provider.settings import oauth2_settings

from revibe._errors import auth, permissions

# -----------------------------------------------------------------------------

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
            raise permissions.PermissionError("You do not have access for this request type")

        raise auth.NoAuthenticationError("Could not identify a session or a request access token")

    def get_scopes(self, request, view):
        try:
            return getattr(view, "required_alternate_scopes")
        except AttributeError:
            raise ImproperlyConfigured("Must specify 'required_alternate_scopes'")

class TokenOrSessionUserPermissions(BasePermission):
    pass

class AdminOnlyTokenPermissions(BasePermission):

    def has_permission(self, request, view):
        token = request.auth

        if hasattr(token, "scope"):
            user = AccessToken.objects.get(token=token).user
            if not user:
                raise auth.NoAuthenticationError("Could not identify this token's user")

            required_alternate_scopes = self.get_scopes(request, view)

            m = request.method.upper()
            if m in required_alternate_scopes:
                for alt in required_alternate_scopes[m]:
                    if token.is_valid(alt) and user.is_staff:
                        return True
            
            raise permissions.PermissionError("You do not have access for this request type")
        
        raise auth.NoAuthenticationError("Could not identify a session or a request access token")

    def get_scopes(self, request, view):
        try:
            return getattr(view, "required_alternate_scopes")
        except AttributeError:
            raise ImproperlyConfigured("Must specify 'required_alternate_scopes'")
