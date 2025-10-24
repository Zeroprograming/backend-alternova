"""
URLs de presentación para la capa de presentación.
Define las rutas de la API para la interfaz de usuario.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views.user_views import UserPresentationViewSet
from ..views.auth_views import (
    AuthPresentationViewSet,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    TokenVerifyView,
    LogoutView,
)
from ..views.role_views import RolePresentationViewSet

# Crear routers para las vistas
user_router = DefaultRouter()
user_router.register(r"users", UserPresentationViewSet, basename="user")

auth_router = DefaultRouter()
auth_router.register(r"auth", AuthPresentationViewSet, basename="auth")

role_router = DefaultRouter()
role_router.register(r"roles", RolePresentationViewSet, basename="role")

# URLs principales
urlpatterns = [
    # URLs para gestión de usuarios
    path("", include(user_router.urls)),
    # URLs para autenticación
    path("", include(auth_router.urls)),
    # URLs para gestión de roles
    path("", include(role_router.urls)),
    # URLs específicas de autenticación JWT
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="auth_login"),
    path("auth/refresh/", CustomTokenRefreshView.as_view(), name="auth_refresh"),
    path("auth/verify/", TokenVerifyView.as_view(), name="auth_verify"),
    path("auth/logout/", LogoutView.as_view(), name="auth_logout"),
]
