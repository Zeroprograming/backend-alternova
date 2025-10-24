"""
URLs para gestión de roles y usuarios.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .role_views import RoleManagementViewSet, UserManagementViewSet

# Crear routers para las vistas de roles
role_router = DefaultRouter()
role_router.register(r"roles", RoleManagementViewSet, basename="role-management")

user_management_router = DefaultRouter()
user_management_router.register(
    r"users", UserManagementViewSet, basename="user-management"
)

urlpatterns = [
    # URLs para gestión de roles
    path("admin/", include(role_router.urls)),
    # URLs para gestión de usuarios
    path("admin/", include(user_management_router.urls)),
]
