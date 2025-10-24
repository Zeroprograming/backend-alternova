"""
Vistas que demuestran el uso de consultas ORM avanzadas con validaciones de negocio.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.contrib.auth import get_user_model
from ...application.services.advanced_orm_services import AdvancedORMService
from ...application.services.optimized_query_services import OptimizedQueryService
from users.presentation.permissions.permissions import (
    IsAdminUser,
    IsTeacherUser,
    IsStudentUser,
)
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class AdvancedORMViewSet(viewsets.ViewSet):
    """
    ViewSet que demuestra consultas ORM avanzadas con validaciones de negocio.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Validar elegibilidad de inscripción",
        description="Valida la elegibilidad de un estudiante para inscribirse en una materia usando consultas ORM avanzadas",
        tags=["ORM Avanzado"],
        parameters=[
            OpenApiParameter(
                name="student_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="ID del estudiante",
                required=True,
            ),
            OpenApiParameter(
                name="subject_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="ID de la materia",
                required=True,
            ),
        ],
    )
    @action(detail=False, methods=["get"])
    def validate_enrollment_eligibility(self, request):
        """
        Valida la elegibilidad de inscripción usando Subquery y Exists.

        Endpoint: GET /api/orm-advanced/validate-enrollment-eligibility/
        """
        student_id = request.query_params.get("student_id")
        subject_id = request.query_params.get("subject_id")

        if not student_id or not subject_id:
            return Response(
                {"error": "student_id y subject_id son requeridos"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            student_id = int(student_id)
            subject_id = int(subject_id)
        except ValueError:
            return Response(
                {"error": "Los IDs deben ser números válidos"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            student = User.objects.get(
                id=student_id, user_type="student", is_active=True
            )
            from subjects.models import Subject

            subject = Subject.objects.get(id=subject_id, is_active=True)
        except User.DoesNotExist:
            return Response(
                {"error": "Estudiante no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Subject.DoesNotExist:
            return Response(
                {"error": "Materia no encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Validar permisos
        if not request.user.is_staff and request.user.id != student_id:
            return Response(
                {"error": "No tienes permisos para validar esta inscripción"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            is_eligible, message, details = (
                AdvancedORMService.validate_student_enrollment_eligibility(
                    student, subject
                )
            )

            return Response(
                {
                    "is_eligible": is_eligible,
                    "message": message,
                    "details": details,
                    "student": {
                        "id": student.id,
                        "name": student.full_name,
                        "username": student.username,
                        "available_credits": student.available_credits,
                    },
                    "subject": {
                        "id": subject.id,
                        "code": subject.code,
                        "name": subject.name,
                        "credits": subject.credits,
                        "max_students": subject.max_students,
                    },
                }
            )

        except Exception as e:
            logger.error(f"Error validando elegibilidad de inscripción: {e}")
            return Response(
                {"error": "Error interno validando elegibilidad"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Métricas de rendimiento del profesor",
        description="Obtiene métricas detalladas de rendimiento de un profesor usando consultas ORM avanzadas",
        tags=["ORM Avanzado"],
        parameters=[
            OpenApiParameter(
                name="teacher_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="ID del profesor",
                required=True,
            ),
        ],
    )
    @action(detail=False, methods=["get"])
    def teacher_performance_metrics(self, request):
        """
        Obtiene métricas de rendimiento del profesor usando annotate y Case/When.

        Endpoint: GET /api/orm-advanced/teacher-performance-metrics/
        """
        teacher_id = request.query_params.get("teacher_id")

        if not teacher_id:
            return Response(
                {"error": "teacher_id es requerido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            teacher_id = int(teacher_id)
        except ValueError:
            return Response(
                {"error": "teacher_id debe ser un número válido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            teacher = User.objects.get(
                id=teacher_id, user_type="teacher", is_active=True
            )
        except User.DoesNotExist:
            return Response(
                {"error": "Profesor no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Validar permisos
        if not request.user.is_staff and request.user.id != teacher_id:
            return Response(
                {"error": "No tienes permisos para ver estas métricas"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            performance_data = AdvancedORMService.get_teacher_performance_metrics(
                teacher
            )
            return Response(performance_data)

        except Exception as e:
            logger.error(f"Error obteniendo métricas de rendimiento: {e}")
            return Response(
                {"error": "Error interno obteniendo métricas"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Progreso académico del estudiante",
        description="Obtiene el progreso académico detallado de un estudiante usando consultas ORM avanzadas",
        tags=["ORM Avanzado"],
        parameters=[
            OpenApiParameter(
                name="student_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="ID del estudiante",
                required=True,
            ),
        ],
    )
    @action(detail=False, methods=["get"])
    def student_academic_progress(self, request):
        """
        Obtiene el progreso académico del estudiante usando Subquery y annotate.

        Endpoint: GET /api/orm-advanced/student-academic-progress/
        """
        student_id = request.query_params.get("student_id")

        if not student_id:
            return Response(
                {"error": "student_id es requerido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            student_id = int(student_id)
        except ValueError:
            return Response(
                {"error": "student_id debe ser un número válido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            student = User.objects.get(
                id=student_id, user_type="student", is_active=True
            )
        except User.DoesNotExist:
            return Response(
                {"error": "Estudiante no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Validar permisos
        if not request.user.is_staff and request.user.id != student_id:
            return Response(
                {"error": "No tienes permisos para ver este progreso"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            progress_data = AdvancedORMService.get_student_academic_progress(student)
            return Response(progress_data)

        except Exception as e:
            logger.error(f"Error obteniendo progreso académico: {e}")
            return Response(
                {"error": "Error interno obteniendo progreso"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Análisis de inscripciones de materia",
        description="Obtiene análisis detallado de inscripciones de una materia usando consultas ORM avanzadas",
        tags=["ORM Avanzado"],
        parameters=[
            OpenApiParameter(
                name="subject_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="ID de la materia",
                required=True,
            ),
        ],
    )
    @action(detail=False, methods=["get"])
    def subject_enrollment_analytics(self, request):
        """
        Obtiene análisis de inscripciones de una materia usando annotate y Subquery.

        Endpoint: GET /api/orm-advanced/subject-enrollment-analytics/
        """
        subject_id = request.query_params.get("subject_id")

        if not subject_id:
            return Response(
                {"error": "subject_id es requerido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            subject_id = int(subject_id)
        except ValueError:
            return Response(
                {"error": "subject_id debe ser un número válido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            from subjects.models import Subject

            subject = Subject.objects.get(id=subject_id, is_active=True)
        except Subject.DoesNotExist:
            return Response(
                {"error": "Materia no encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Validar permisos
        if not request.user.is_staff and not (
            request.user.is_teacher and subject.teacher == request.user
        ):
            return Response(
                {"error": "No tienes permisos para ver este análisis"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            analytics_data = AdvancedORMService.get_subject_enrollment_analytics(
                subject
            )
            return Response(analytics_data)

        except Exception as e:
            logger.error(f"Error obteniendo análisis de inscripciones: {e}")
            return Response(
                {"error": "Error interno obteniendo análisis"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Datos optimizados del dashboard",
        description="Obtiene datos optimizados para el dashboard usando prefetch_related",
        tags=["ORM Avanzado"],
    )
    @action(
        detail=False, methods=["get"], permission_classes=[IsAuthenticated, IsAdminUser]
    )
    def optimized_dashboard_data(self, request):
        """
        Obtiene datos optimizados del dashboard usando prefetch_related.

        Endpoint: GET /api/orm-advanced/optimized-dashboard-data/
        """
        try:
            dashboard_data = OptimizedQueryService.get_optimized_dashboard_data()
            return Response(dashboard_data)

        except Exception as e:
            logger.error(f"Error obteniendo datos del dashboard: {e}")
            return Response(
                {"error": "Error interno obteniendo datos del dashboard"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Estudiantes con información académica completa",
        description="Obtiene estudiantes con información académica completa usando prefetch_related",
        tags=["ORM Avanzado"],
    )
    @action(
        detail=False, methods=["get"], permission_classes=[IsAuthenticated, IsAdminUser]
    )
    def students_with_complete_info(self, request):
        """
        Obtiene estudiantes con información completa usando prefetch_related.

        Endpoint: GET /api/orm-advanced/students-with-complete-info/
        """
        try:
            students = OptimizedQueryService.get_students_with_complete_academic_info()

            # Paginar resultados
            page = self.paginate_queryset(students)
            if page is not None:
                from users.presentation.serializers.user_serializers import (
                    UserSerializer,
                )

                serializer = UserSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            from users.presentation.serializers.user_serializers import UserSerializer

            serializer = UserSerializer(students, many=True)
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Error obteniendo estudiantes con información completa: {e}")
            return Response(
                {"error": "Error interno obteniendo información de estudiantes"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Actualización masiva de créditos",
        description="Actualiza masivamente los créditos de estudiantes usando consultas optimizadas",
        tags=["ORM Avanzado"],
    )
    @action(
        detail=False,
        methods=["post"],
        permission_classes=[IsAuthenticated, IsAdminUser],
    )
    def bulk_update_student_credits(self, request):
        """
        Actualiza masivamente los créditos de estudiantes usando consultas optimizadas.

        Endpoint: POST /api/orm-advanced/bulk-update-student-credits/
        """
        try:
            updated_count = OptimizedQueryService.bulk_update_student_credits()

            return Response(
                {
                    "message": f"Actualizados créditos de {updated_count} estudiantes",
                    "updated_count": updated_count,
                }
            )

        except Exception as e:
            logger.error(f"Error actualizando créditos masivamente: {e}")
            return Response(
                {"error": "Error interno actualizando créditos"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Estadísticas masivas de materias",
        description="Calcula estadísticas masivas de materias usando consultas optimizadas",
        tags=["ORM Avanzado"],
    )
    @action(
        detail=False, methods=["get"], permission_classes=[IsAuthenticated, IsAdminUser]
    )
    def bulk_subject_statistics(self, request):
        """
        Calcula estadísticas masivas de materias usando consultas optimizadas.

        Endpoint: GET /api/orm-advanced/bulk-subject-statistics/
        """
        try:
            statistics = OptimizedQueryService.bulk_calculate_subject_statistics()
            return Response(
                {"statistics": statistics, "total_subjects": len(statistics)}
            )

        except Exception as e:
            logger.error(f"Error calculando estadísticas masivas: {e}")
            return Response(
                {"error": "Error interno calculando estadísticas"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
