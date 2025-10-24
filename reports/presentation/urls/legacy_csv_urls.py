"""
URLs para generación de reportes CSV.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views.legacy_csv_views import CSVReportViewSet

# Crear router para las vistas de reportes CSV
csv_router = DefaultRouter()
csv_router.register(r"csv", CSVReportViewSet, basename="csv-reports")

urlpatterns = [
    # URLs para reportes CSV
    path("", include(csv_router.urls)),
]
