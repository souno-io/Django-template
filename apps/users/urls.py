from django.urls import path, include

from rest_framework import routers
from . import views as users_views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

api_root = routers.DefaultRouter()
# api_root.register(r'BedConfig', ra4odi_views.BedConfigViewSet, basename='BedConfig-List')

app_name = 'users'
urlpatterns = [
    path('api', include(api_root.urls)),
    path('logout', users_views.logout, name='userInfo'),
    path('userInfo', users_views.userinfo, name='userInfo'),
    path('has_perm/<str:menu_code>/', users_views.has_menu, name='has_perm'),
    path('router', users_views.user_menu, name='user_menu'),
    path('login', TokenObtainPairView.as_view(), name='token_login'),
    # path('login', obtain_jwt_token, name='token_login'),
    path('refresh', TokenRefreshView.as_view(), name='token_refresh'),
    # path('refresh', refresh_jwt_token, name='token_refresh'),
    path('verify', TokenVerifyView.as_view(), name='token_verify'),
]