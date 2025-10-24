"""
Vistas académicas para estudiantes y profesores.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from ...application.services.legacy_academic_services import AcademicService
from ...infrastructure.models import Subject, Enrollment
import logging

logger = logging.getLogger(__name__)


class StudentAcademicViewSet(viewsets.ViewSet):
    """ViewSet para funcionalidades académicas de estudiantes."""

    @extend_schema(
        summary="Resumen académico del estudiante",
        description="Obtiene el resumen académico completo del estudiante actual",
        tags=["Estudiante - Académico"],
    )
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def academic_summary(self, request):
        """Obtiene resumen académico del estudiante."""
        if not request.user.is_student:
            return Response(
                {"error": "Solo estudiantes pueden acceder a esta información"},
                status=status.HTTP_403_FORBIDDEN,
            )

        summary = AcademicService.get_student_academic_summary(request.user)
        return Response(summary)

    @extend_schema(
        summary="Histórico académico",
        description="Obtiene el histórico académico completo del estudiante",
        tags=["Estudiante - Académico"],
    )
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def academic_history(self, request):
        """Obtiene histórico académico del estudiante."""
        if not request.user.is_student:
            return Response(
                {"error": "Solo estudiantes pueden acceder a esta información"},
                status=status.HTTP_403_FORBIDDEN,
            )

        history = request.user.get_academic_history()

        # Serializar datos
        history_data = []
        for enrollment in history:
            history_data.append(
                {
                    "id": enrollment.id,
                    "subject_code": enrollment.subject.code,
                    "subject_name": enrollment.subject.name,
                    "credits": enrollment.subject.credits,
                    "grade": (
                        float(enrollment.final_grade)
                        if enrollment.final_grade
                        else None
                    ),
                    "status": enrollment.status,
                    "academic_year": enrollment.academic_year,
                    "semester": enrollment.semester,
                    "enrolled_at": enrollment.enrolled_at,
                }
            )

        return Response(
            {
                "student": {
                    "id": request.user.id,
                    "name": request.user.full_name,
                    "username": request.user.username,
                },
                "academic_history": history_data,
                "cumulative_average": request.user.get_cumulative_average(),
            }
        )

    @extend_schema(
        summary="Promedio acumulado",
        description="Obtiene el promedio acumulado del estudiante",
        tags=["Estudiante - Académico"],
    )
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def cumulative_average(self, request):
        """Obtiene promedio acumulado del estudiante."""
        if not request.user.is_student:
            return Response(
                {"error": "Solo estudiantes pueden acceder a esta información"},
                status=status.HTTP_403_FORBIDDEN,
            )

        average = request.user.get_cumulative_average()
        return Response({"cumulative_average": average})

    @extend_schema(
        summary="Créditos disponibles",
        description="Obtiene información de créditos del estudiante",
        tags=["Estudiante - Académico"],
    )
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def credits_info(self, request):
        """Obtiene información de créditos del estudiante."""
        if not request.user.is_student:
            return Response(
                {"error": "Solo estudiantes pueden acceder a esta información"},
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response(
            {
                "max_credits_per_semester": request.user.max_credits_per_semester,
                "current_semester_credits": request.user.current_semester_credits,
                "available_credits": request.user.available_credits,
                "academic_year": request.user.academic_year,
            }
        )


class TeacherAcademicViewSet(viewsets.ViewSet):
    """ViewSet para funcionalidades académicas de profesores."""

    @extend_schema(
        summary="Resumen de materias del profesor",
        description="Obtiene el resumen de todas las materias del profesor",
        tags=["Profesor - Académico"],
    )
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def subjects_summary(self, request):
        """Obtiene resumen de materias del profesor."""
        if not request.user.is_teacher:
            return Response(
                {"error": "Solo profesores pueden acceder a esta información"},
                status=status.HTTP_403_FORBIDDEN,
            )

        summary = AcademicService.get_teacher_subjects_summary(request.user)
        return Response(summary)

    @extend_schema(
        summary="Estudiantes inscritos por materia",
        description="Obtiene lista de estudiantes inscritos en una materia específica",
        tags=["Profesor - Académico"],
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
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def enrolled_students(self, request):
        """Obtiene estudiantes inscritos en una materia."""
        if not request.user.is_teacher:
            return Response(
                {"error": "Solo profesores pueden acceder a esta información"},
                status=status.HTTP_403_FORBIDDEN,
            )

        subject_id = request.query_params.get("subject_id")
        if not subject_id:
            return Response(
                {"error": "Se requiere subject_id"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            subject = Subject.objects.get(id=subject_id, teacher=request.user)
        except Subject.DoesNotExist:
            return Response(
                {"error": "Materia no encontrada o no tienes permisos"},
                status=status.HTTP_404_NOT_FOUND,
            )

        enrollments = Enrollment.objects.filter(
            subject=subject, is_active=True
        ).select_related("student")

        students_data = []
        for enrollment in enrollments:
            students_data.append(
                {
                    "enrollment_id": enrollment.id,
                    "student_id": enrollment.student.id,
                    "student_name": enrollment.student.full_name,
                    "student_username": enrollment.student.username,
                    "grade": (
                        float(enrollment.final_grade)
                        if enrollment.final_grade
                        else None
                    ),
                    "status": enrollment.status,
                    "enrolled_at": enrollment.enrolled_at,
                }
            )

        return Response(
            {
                "subject": {
                    "id": subject.id,
                    "code": subject.code,
                    "name": subject.name,
                    "credits": subject.credits,
                    "is_finished": subject.is_finished,
                },
                "students": students_data,
                "total_students": len(students_data),
                "graded_students": len(
                    [s for s in students_data if s["grade"] is not None]
                ),
                "ungraded_students": len(
                    [s for s in students_data if s["grade"] is None]
                ),
            }
        )

    @extend_schema(
        summary="Finalizar materia",
        description="Finaliza una materia (solo si todos los estudiantes están calificados)",
        tags=["Profesor - Académico"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "subject_id": {
                        "type": "integer",
                        "description": "ID de la materia",
                    },
                },
                "required": ["subject_id"],
            }
        },
    )
    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def finish_subject(self, request):
        """Finaliza una materia."""
        if not request.user.is_teacher:
            return Response(
                {"error": "Solo profesores pueden finalizar materias"},
                status=status.HTTP_403_FORBIDDEN,
            )

        subject_id = request.data.get("subject_id")
        if not subject_id:
            return Response(
                {"error": "Se requiere subject_id"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            subject = Subject.objects.get(id=subject_id, teacher=request.user)
        except Subject.DoesNotExist:
            return Response(
                {"error": "Materia no encontrada o no tienes permisos"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            finished_subject = AcademicService.finish_subject(subject, request.user)
            return Response(
                {
                    "message": f"Materia {finished_subject.code} finalizada exitosamente",
                    "subject": {
                        "id": finished_subject.id,
                        "code": finished_subject.code,
                        "name": finished_subject.name,
                        "is_finished": finished_subject.is_finished,
                    },
                }
            )

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
