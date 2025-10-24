"""
Vistas para generación de reportes CSV.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.contrib.auth import get_user_model
from .csv_services import CSVReportService
from users.permissions import IsAdminUser, IsStudentUser, IsTeacherUser
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class CSVReportViewSet(viewsets.ViewSet):
    """
    ViewSet para generación de reportes CSV.
    Endpoints protegidos para estudiantes, profesores y administradores.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Generar reporte CSV de estudiante",
        description="Genera un reporte CSV completo con información académica del estudiante",
        tags=["Reportes CSV"],
        parameters=[
            OpenApiParameter(
                name="student_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="ID del estudiante",
                required=True,
            ),
        ],
    )
    @action(detail=False, methods=["get"], url_path="estudiante/(?P<student_id>[^/.]+)")
    def generate_student_report(self, request, student_id=None):
        """
        Genera reporte CSV para un estudiante específico.

        Endpoint: GET /api/reports/csv/estudiante/{student_id}/

        Permisos:
        - El propio estudiante puede generar su reporte
        - Los administradores pueden generar cualquier reporte
        """
        if not student_id:
            return Response(
                {"error": "ID de estudiante requerido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            student_id = int(student_id)
        except ValueError:
            return Response(
                {"error": "ID de estudiante debe ser un número válido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            csv_response = CSVReportService.generate_student_report(
                student_id, request.user
            )
            return csv_response

        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error generando reporte de estudiante: {e}")
            return Response(
                {"error": "Error interno generando el reporte"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Generar reporte CSV de profesor",
        description="Genera un reporte CSV completo con información académica del profesor",
        tags=["Reportes CSV"],
        parameters=[
            OpenApiParameter(
                name="teacher_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="ID del profesor",
                required=True,
            ),
        ],
    )
    @action(detail=False, methods=["get"], url_path="profesor/(?P<teacher_id>[^/.]+)")
    def generate_teacher_report(self, request, teacher_id=None):
        """
        Genera reporte CSV para un profesor específico.

        Endpoint: GET /api/reports/csv/profesor/{teacher_id}/

        Permisos:
        - El propio profesor puede generar su reporte
        - Los administradores pueden generar cualquier reporte
        """
        if not teacher_id:
            return Response(
                {"error": "ID de profesor requerido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            teacher_id = int(teacher_id)
        except ValueError:
            return Response(
                {"error": "ID de profesor debe ser un número válido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            csv_response = CSVReportService.generate_teacher_report(
                teacher_id, request.user
            )
            return csv_response

        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error generando reporte de profesor: {e}")
            return Response(
                {"error": "Error interno generando el reporte"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Generar reporte CSV general del sistema",
        description="Genera un reporte CSV con estadísticas generales del sistema (solo administradores)",
        tags=["Reportes CSV"],
    )
    @action(
        detail=False, methods=["get"], permission_classes=[IsAuthenticated, IsAdminUser]
    )
    def generate_general_report(self, request):
        """
        Genera reporte CSV general del sistema.

        Endpoint: GET /api/reports/csv/general/

        Permisos:
        - Solo administradores pueden generar este reporte
        """
        try:
            csv_response = CSVReportService.generate_general_report(request.user)
            return csv_response

        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"Error generando reporte general: {e}")
            return Response(
                {"error": "Error interno generando el reporte"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Generar mi reporte CSV personal",
        description="Genera un reporte CSV personal según el rol del usuario autenticado",
        tags=["Reportes CSV"],
    )
    @action(detail=False, methods=["get"])
    def generate_my_report(self, request):
        """
        Genera reporte CSV personal según el rol del usuario.

        Endpoint: GET /api/reports/csv/mi-reporte/

        Comportamiento:
        - Estudiantes: Genera su reporte académico
        - Profesores: Genera su reporte de materias y estudiantes
        - Administradores: Genera reporte general del sistema
        """
        try:
            user = request.user

            if user.is_student:
                # Estudiante genera su propio reporte
                csv_response = CSVReportService.generate_student_report(user.id, user)
                return csv_response

            elif user.is_teacher:
                # Profesor genera su propio reporte
                csv_response = CSVReportService.generate_teacher_report(user.id, user)
                return csv_response

            elif user.is_staff:
                # Administrador genera reporte general
                csv_response = CSVReportService.generate_general_report(user)
                return csv_response

            else:
                return Response(
                    {"error": "Tipo de usuario no válido para generar reportes"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            logger.error(f"Error generando reporte personal: {e}")
            return Response(
                {"error": "Error interno generando el reporte personal"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Listar reportes disponibles",
        description="Lista los tipos de reportes disponibles según el rol del usuario",
        tags=["Reportes CSV"],
    )
    @action(detail=False, methods=["get"])
    def available_reports(self, request):
        """
        Lista los tipos de reportes disponibles según el rol del usuario.

        Endpoint: GET /api/reports/csv/disponibles/
        """
        user = request.user
        available_reports = []

        if user.is_student:
            available_reports = [
                {
                    "type": "student_report",
                    "name": "Mi Reporte Académico",
                    "description": "Reporte completo con mi información académica, materias inscritas y calificaciones",
                    "endpoint": f"/api/reports/csv/estudiante/{user.id}/",
                    "my_report_endpoint": "/api/reports/csv/mi-reporte/",
                }
            ]
        elif user.is_teacher:
            available_reports = [
                {
                    "type": "teacher_report",
                    "name": "Mi Reporte de Profesor",
                    "description": "Reporte con mis materias asignadas, estudiantes y calificaciones",
                    "endpoint": f"/api/reports/csv/profesor/{user.id}/",
                    "my_report_endpoint": "/api/reports/csv/mi-reporte/",
                }
            ]
        elif user.is_staff:
            available_reports = [
                {
                    "type": "student_report",
                    "name": "Reporte de Estudiante",
                    "description": "Reporte académico de cualquier estudiante",
                    "endpoint": "/api/reports/csv/estudiante/{student_id}/",
                    "example": "/api/reports/csv/estudiante/1/",
                },
                {
                    "type": "teacher_report",
                    "name": "Reporte de Profesor",
                    "description": "Reporte académico de cualquier profesor",
                    "endpoint": "/api/reports/csv/profesor/{teacher_id}/",
                    "example": "/api/reports/csv/profesor/1/",
                },
                {
                    "type": "general_report",
                    "name": "Reporte General del Sistema",
                    "description": "Estadísticas generales del sistema académico",
                    "endpoint": "/api/reports/csv/general/",
                    "my_report_endpoint": "/api/reports/csv/mi-reporte/",
                },
            ]

        return Response(
            {
                "user_role": user.user_type,
                "user_name": user.full_name,
                "available_reports": available_reports,
                "total_reports": len(available_reports),
            }
        )
