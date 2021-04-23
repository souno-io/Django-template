from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from rest_framework_simplejwt.settings import api_settings

User = get_user_model()


class SSOJWTAuthentication(JWTAuthentication):

    @classmethod
    def get_token_user(cls,user_id, user_info):
        try:
            user = User.objects.get(**{api_settings.USER_ID_FIELD: user_id})
        except User.DoesNotExist:
            user_data = dict(
            (k, user_info.get(k, '')) for k in ['username', 'first_name', 'last_name', 'email'])
            user = User.objects.create_user(**{api_settings.USER_ID_FIELD: user_id, **user_data})
            user.set_unusable_password()
        return user

    def get_user(self, validated_token):
        """
        Attempts to find and return a user using the given validated token.
        """
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise InvalidToken(_('Token contained no recognizable user identification'))
        
        user = self.get_token_user(user_id, validated_token['user_info'])
    
        if not user.is_active:
            raise AuthenticationFailed(_('User is inactive'), code='user_inactive')

        return user
