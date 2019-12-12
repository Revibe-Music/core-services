from django.core.exceptions import ImproperlyConfigured
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission
from oauth2_provider.settings import oauth2_settings

from artist_portal._helpers.debug import debug_print

class TokenOrSessionAuthentication(BasePermission):

    def has_permission(self ,request, view):
        token = request.auth
        debug_print('token: {}'.format(token))

        if (not token) and (request.session.session_key != None):
            return True

        if hasattr(token, "scope"):
            debug_print("Token has a 'scope'")
            required_alternate_scopes = self.get_scopes(request, view)

            m = request.method.upper()
            if m in required_alternate_scopes:
                for alt in required_alternate_scopes[m]:
                    if token.is_valid(alt):
                        debug_print('user has scope {} for {} request'.format(alt, m))
                        return True
            return False

        assert False, ("everything fucked up")

    def get_scopes(self, request, view):
        try:
            return getattr(view, "required_alternate_scopes")
        except AttributeError:
            raise ImproperlyConfigured("This one fucked up too")
