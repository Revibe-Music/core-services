from rest_framework.authentication import SessionAuthentication

# -----------------------------------------------------------------------------

# https://stackoverflow.com/questions/30871033/django-rest-framework-remove-csrf
class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening
