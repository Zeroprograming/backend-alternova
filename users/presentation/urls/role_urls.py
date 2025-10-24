"""
URLs de roles para la capa de presentación.
Define las rutas de gestión de roles de la API.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views.role_views import RolePresentationViewSet

# Crear router para vistas de roles
role_router = DefaultRouter()
role_router.register(r"roles", RolePresentationViewSet, basename="role")

# URLs de roles
urlpatterns = [
    # URLs del router de roles
    path("", include(role_router.urls)),
]
