from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import TokenPairSerializer


class SSOTokenObtainView(TokenObtainPairView):
    serializer_class = TokenPairSerializer


class SSOTokenRefreshView(TokenRefreshView):
    pass
