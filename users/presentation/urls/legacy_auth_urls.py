"""
URLs para autenticación.
"""

from django.urls import path
from ..views.legacy_auth_views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    TokenVerifyView,
    LogoutView,
    ActiveSessionsView,
    RevokeSessionView,
)

urlpatterns = [
    # Autenticación JWT
    path("login/", CustomTokenObtainPairView.as_view(), name="auth_login"),
    path("refresh/", CustomTokenRefreshView.as_view(), name="auth_refresh"),
    path("verify/", TokenVerifyView.as_view(), name="auth_verify"),
    path("logout/", LogoutView.as_view(), name="auth_logout"),
    # Gestión de sesiones
    path("sessions/", ActiveSessionsView.as_view(), name="active_sessions"),
    path(
        "sessions/<int:session_id>/revoke/",
        RevokeSessionView.as_view(),
        name="revoke_session",
    ),
]
