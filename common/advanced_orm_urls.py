"""
URLs para vistas que demuestran consultas ORM avanzadas.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .advanced_orm_views import AdvancedORMViewSet

# Crear router para las vistas ORM avanzadas
advanced_orm_router = DefaultRouter()
advanced_orm_router.register(
    r"orm-advanced", AdvancedORMViewSet, basename="advanced-orm"
)

urlpatterns = [
    # URLs para consultas ORM avanzadas
    path("", include(advanced_orm_router.urls)),
]
