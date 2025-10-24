"""URLs para reportes."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views.legacy_views import ReportViewSet

router = DefaultRouter()
router.register(r"reports", ReportViewSet)

urlpatterns = [
    path("", include(router.urls)),
    # URLs para reportes CSV
    path("", include("reports.presentation.urls.legacy_csv_urls")),
]
