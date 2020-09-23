from rest_framework import authentication
from main.models import Token


class TokenAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        try:
            return Token.objects.get(token=token).user, None
        except Token.DoesNotExist:
            pass
        return None
