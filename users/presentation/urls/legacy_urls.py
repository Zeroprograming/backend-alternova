"""
URLs para la app users.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views.legacy_views import UserViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),
    # URLs para gestión de roles y usuarios administrativos
    path("", include("users.presentation.urls.legacy_role_urls")),
]
