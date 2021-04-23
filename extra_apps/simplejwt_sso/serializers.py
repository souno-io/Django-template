from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class TokenUserSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'groups', 'permissions')

    def get_groups(self, user):
        return list(user.groups.all().values_list('name', flat=True))

    def get_permissions(self, user):
        return list(user.user_permissions.all().values_list('codename', flat=True))


class TokenPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        user_data = dict()
        token = super().validate(attrs)
        refresh = self.get_token(self.user)

        token['refresh'] = str(refresh)
        token['access'] = str(refresh.access_token)

        user_data['token'] = token
        user_data['user_info'] = TokenUserSerializer(self.user).data
        return user_data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add extra user info
        token['user_info'] = TokenUserSerializer(user).data
        return token
