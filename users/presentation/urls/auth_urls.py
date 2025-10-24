"""
URLs de autenticación para la capa de presentación.
Define las rutas de autenticación de la API.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views.auth_views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    TokenVerifyView,
    LogoutView,
    AuthPresentationViewSet,
)

# Crear router para vistas de autenticación
auth_router = DefaultRouter()
auth_router.register(r"auth", AuthPresentationViewSet, basename="auth")

# URLs de autenticación
urlpatterns = [
    # URLs del router de autenticación
    path("", include(auth_router.urls)),
    # URLs específicas de autenticación JWT
    path("login/", CustomTokenObtainPairView.as_view(), name="auth_login"),
    path("refresh/", CustomTokenRefreshView.as_view(), name="auth_refresh"),
    path("verify/", TokenVerifyView.as_view(), name="auth_verify"),
    path("logout/", LogoutView.as_view(), name="auth_logout"),
]
