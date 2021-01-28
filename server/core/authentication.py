"""
登录验证模块
"""
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed


def expires_in(token):
    """Token's left time"""
    time_elapsed = timezone.now() - token.created
    left_time = timedelta(seconds=settings.TOKEN_EXPIRED_AFTER_SECONDS) - time_elapsed
    return left_time


def is_token_expired(token):
    """Token checker if token expired or not"""
    return expires_in(token) < timedelta(seconds=0)


class ExpiringTokenAuthentication(TokenAuthentication):
    """
    If token is expired then it will be removed
    and new one with different key will be created
    """

    def authenticate_credentials(self, key):
        try:
            token = Token.objects.get(key=key)
        except Token.DoesNotExist:
            raise AuthenticationFailed("Invalid Token")

        if not token.user.is_active:
            raise AuthenticationFailed("User is not active")

        is_expired = is_token_expired(token)
        if is_expired:
            token.delete()
            raise AuthenticationFailed("The Token is expired")

        return token.user, token


if settings.DEBUG:
    Authentications = [ExpiringTokenAuthentication, SessionAuthentication]
else:
    Authentications = [ExpiringTokenAuthentication]
