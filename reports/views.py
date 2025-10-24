"""
Views para reportes.
SOLO enrutamiento - Toda la lógica en ReportService.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .models import Report
from .serializers import ReportSerializer, ReportCreateSerializer
from .services import ReportService
import logging

logger = logging.getLogger(__name__)


class ReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de reportes con JWT y validaciones.
    La lógica compleja está delegada en ReportService.
    """

    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filtrar por usuario si no es admin."""
        if self.request.user.is_staff:
            return self.queryset.filter(is_active=True)
        return self.queryset.filter(generated_by=self.request.user, is_active=True)

    @extend_schema(
        summary="Listar reportes",
        description="Lista reportes del usuario actual (requiere JWT)",
        tags=["Reportes"],
        parameters=[
            OpenApiParameter(
                name="report_type",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filtrar por tipo de reporte",
                required=False,
                enum=["grades", "attendance", "enrollments", "users", "custom"],
            ),
            OpenApiParameter(
                name="status",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filtrar por estado",
                required=False,
                enum=["pending", "processing", "completed", "failed"],
            ),
        ],
    )
    def list(self, request):
        """Enrutar a service para listar reportes."""
        report_type = request.query_params.get("report_type")
        status_filter = request.query_params.get("status")

        queryset = ReportService.list_reports(request.user, report_type, status_filter)

        page = self.paginate_queryset(queryset)
        if page:
            serializer = ReportSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ReportSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Obtener reporte",
        description="Obtiene detalles de un reporte (requiere JWT)",
        tags=["Reportes"],
    )
    def retrieve(self, request, pk=None):
        """Enrutar a service para obtener reporte."""
        try:
            report = ReportService.retrieve_report(pk, request.user)
            serializer = ReportSerializer(report)
            return Response(serializer.data)

        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="Crear reporte",
        description="Crea una solicitud de reporte (requiere JWT)",
        tags=["Reportes"],
        request=ReportCreateSerializer,
    )
    def create(self, request):
        """Enrutar a service para crear reporte."""
        serializer = ReportCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        report = ReportService.create_report(
            title=serializer.validated_data["title"],
            report_type=serializer.validated_data["report_type"],
            generated_by=request.user,
            filters=serializer.validated_data.get("filters", {}),
        )

        return Response(ReportSerializer(report).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Actualizar reporte",
        description="Actualiza un reporte (solo si está pending, requiere JWT)",
        tags=["Reportes"],
    )
    def update(self, request, pk=None):
        """Enrutar a service para actualizar reporte."""
        report = self.get_object()
        serializer = ReportSerializer(report, data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            updated_report = ReportService.update_report(
                report, serializer.validated_data, request.user
            )
            return Response(ReportSerializer(updated_report).data)

        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Actualizar reporte parcial",
        description="Actualiza campos específicos de un reporte (requiere JWT)",
        tags=["Reportes"],
    )
    def partial_update(self, request, pk=None):
        """Enrutar a service para actualización parcial."""
        report = self.get_object()
        serializer = ReportSerializer(report, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            updated_report = ReportService.update_report(
                report, serializer.validated_data, request.user
            )
            return Response(ReportSerializer(updated_report).data)

        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Eliminar reporte",
        description="Elimina un reporte (requiere JWT)",
        tags=["Reportes"],
    )
    def destroy(self, request, pk=None):
        """Enrutar a service para eliminar reporte."""
        report = self.get_object()

        try:
            ReportService.delete_report(report, request.user)
            return Response(
                {"message": "Reporte eliminado"}, status=status.HTTP_204_NO_CONTENT
            )

        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ========== Acciones personalizadas ==========

    @extend_schema(
        summary="Descargar reporte",
        description="Descarga un reporte generado (requiere JWT)",
        tags=["Reportes"],
    )
    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        """Descargar un reporte generado."""
        report = self.get_object()

        if report.status != "completed":
            return Response(
                {"error": "El reporte aún no está disponible"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not report.file:
            return Response(
                {"error": "No hay archivo disponible"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response({"file_url": report.file.url})
