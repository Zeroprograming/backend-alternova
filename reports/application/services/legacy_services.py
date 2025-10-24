"""Servicios para reportes."""

from django.db import transaction
from ...infrastructure.models import Report
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class ReportService:
    """Servicio para gestión de reportes."""

    @staticmethod
    def list_reports(requesting_user, report_type=None, status_filter=None):
        """
        Lista reportes según permisos.

        Args:
            requesting_user: Usuario que hace la petición
            report_type: Filtro opcional por tipo
            status_filter: Filtro opcional por estado

        Returns:
            QuerySet: Reportes filtrados
        """
        # Admin ve todos, usuarios solo los suyos
        if requesting_user.is_staff:
            queryset = Report.objects.all()
        else:
            queryset = Report.objects.filter(generated_by=requesting_user)

        queryset = queryset.filter(is_active=True)

        # Filtros adicionales
        if report_type:
            queryset = queryset.filter(report_type=report_type)

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.order_by("-created_at")

    @staticmethod
    def retrieve_report(report_id, requesting_user):
        """
        Obtiene un reporte con validaciones.

        Args:
            report_id: ID del reporte
            requesting_user: Usuario que hace la petición

        Returns:
            Report: Reporte encontrado

        Raises:
            ValueError: Si no existe
            PermissionError: Si no tiene acceso
        """
        try:
            report = Report.objects.get(id=report_id, is_active=True)

            # Validar acceso
            if not requesting_user.is_staff and report.generated_by != requesting_user:
                raise PermissionError("Solo puedes ver tus propios reportes")

            return report

        except Report.DoesNotExist:
            raise ValueError("Reporte no encontrado")

    @staticmethod
    @transaction.atomic
    def create_report(title, report_type, generated_by, filters=None):
        """
        Crea un reporte.

        Args:
            title: Título del reporte
            report_type: Tipo de reporte
            generated_by: Usuario que genera el reporte
            filters: Filtros opcionales

        Returns:
            Report: Reporte creado
        """
        report = Report.objects.create(
            title=title,
            report_type=report_type,
            generated_by=generated_by,
            created_by=generated_by,
            filters=filters or {},
            status="pending",
        )
        logger.info(f"Reporte creado: {title} por {generated_by.username}")

        # Disparar tarea asíncrona para generar
        # from .tasks import generate_report_task
        # generate_report_task.delay(report.id)

        return report

    @staticmethod
    @transaction.atomic
    def update_report(report, data, requesting_user):
        """
        Actualiza un reporte.

        Args:
            report: Reporte a actualizar
            data: Nuevos datos
            requesting_user: Usuario que actualiza

        Returns:
            Report: Reporte actualizado

        Raises:
            PermissionError: Si no tiene permisos
            ValueError: Si ya está completado o en progreso
        """
        # Solo el creador o admin pueden actualizar
        if report.generated_by != requesting_user and not requesting_user.is_staff:
            raise PermissionError("Solo puedes actualizar tus propios reportes")

        # No permitir actualizar si ya está completado o procesando
        if report.status in ["completed", "processing"]:
            raise ValueError(
                f"No puedes actualizar un reporte en estado '{report.status}'"
            )

        # Actualizar solo campos permitidos
        allowed_fields = ["title", "filters"]
        for key, value in data.items():
            if key in allowed_fields:
                setattr(report, key, value)

        report.updated_by = requesting_user
        report.save()

        logger.info(f"Reporte {report.id} actualizado por {requesting_user.username}")

        return report

    @staticmethod
    @transaction.atomic
    def delete_report(report, requesting_user):
        """
        Elimina un reporte.

        Args:
            report: Reporte a eliminar
            requesting_user: Usuario que elimina

        Returns:
            Report: Reporte eliminado

        Raises:
            PermissionError: Si no tiene permisos
            ValueError: Si está en progreso
        """
        # Solo el creador o admin pueden eliminar
        if report.generated_by != requesting_user and not requesting_user.is_staff:
            raise PermissionError("Solo puedes eliminar tus propios reportes")

        # No permitir eliminar si está procesando
        if report.status == "processing":
            raise ValueError("No puedes eliminar un reporte en progreso")

        report.soft_delete()

        logger.info(f"Reporte {report.id} eliminado por {requesting_user.username}")

        return report

    @staticmethod
    def mark_as_completed(report, file_path=None):
        """Marca un reporte como completado."""
        report.status = "completed"
        report.completed_at = timezone.now()
        if file_path:
            report.file = file_path
        report.save()
        logger.info(f"Reporte completado: {report.title}")
        return report

    @staticmethod
    def mark_as_failed(report, error_message=None):
        """Marca un reporte como fallido."""
        report.status = "failed"
        report.save()
        logger.error(f"Reporte fallido: {report.title} - {error_message}")
        return report

    @staticmethod
    def generate_grades_report(filters):
        """Genera reporte de notas."""
        logger.info("Generando reporte de notas")
        # Por implementar...
        pass

    @staticmethod
    def generate_enrollments_report(filters):
        """Genera reporte de inscripciones."""
        logger.info("Generando reporte de inscripciones")
        # Por implementar...
        pass
