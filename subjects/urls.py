"""URLs para materias."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubjectViewSet, EnrollmentViewSet

router = DefaultRouter()
router.register(r"subjects", SubjectViewSet)
router.register(r"enrollments", EnrollmentViewSet)

urlpatterns = [
    path("", include(router.urls)),
    # URLs académicas
    path("academic/", include("subjects.academic_urls")),
]
