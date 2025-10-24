"""
URLs para funcionalidades académicas.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .academic_views import StudentAcademicViewSet, TeacherAcademicViewSet

# Crear routers para las vistas académicas
student_router = DefaultRouter()
student_router.register(r"", StudentAcademicViewSet, basename="student-academic")

teacher_router = DefaultRouter()
teacher_router.register(r"", TeacherAcademicViewSet, basename="teacher-academic")

urlpatterns = [
    # URLs para estudiantes
    path("students/", include(student_router.urls)),
    # URLs para profesores
    path("teachers/", include(teacher_router.urls)),
]
